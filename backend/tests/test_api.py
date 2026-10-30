import unittest
import os
from datetime import date, timedelta
from unittest.mock import patch

from sqlalchemy import create_engine, inspect, text
from pydantic import ValidationError
from test_support import TestClient, app, create_account
from app.database.connection import Base, SessionLocal, engine
from app.database.models import Document, Notification
from app.services.ai_service import DocumentAnalysis, analyze_document
from app.services.demo_seed import seed_demo
from app.core.config import Settings
from app.database.compat_migrations import migrate_legacy_sqlite_schema


class CareBridgeApiTests(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        Base.metadata.drop_all(bind=engine)

    def test_demo_mode_allows_both_local_frontend_hostnames(self):
        with patch.dict(os.environ, {"DEMO_MODE": "true", "CORS_ORIGINS": "https://carebridge.example"}):
            origins = Settings().allowed_origins
        self.assertIn("http://localhost:5173", origins)
        self.assertIn("http://127.0.0.1:5173", origins)
        self.assertIn("https://carebridge.example", origins)

    def test_legacy_sqlite_schema_is_upgraded_additively(self):
        legacy_engine = create_engine("sqlite://")
        with legacy_engine.begin() as connection:
            for table in ("patient_profiles", "caregiver_relationships", "documents",
                          "extracted_document_data", "notifications"):
                connection.execute(text(f'CREATE TABLE "{table}" (id INTEGER PRIMARY KEY)'))
            connection.execute(text("INSERT INTO patient_profiles (id) VALUES (1)"))

        migrate_legacy_sqlite_schema(legacy_engine)
        inspector = inspect(legacy_engine)
        profile = {column["name"] for column in inspector.get_columns("patient_profiles")}
        notifications = {column["name"] for column in inspector.get_columns("notifications")}
        self.assertTrue({"created_at", "updated_at"}.issubset(profile))
        self.assertTrue({"dedupe_key", "updated_at"}.issubset(notifications))
        self.assertIsNotNone(legacy_engine.connect().execute(text("SELECT created_at FROM patient_profiles WHERE id=1")).scalar_one())
        legacy_engine.dispose()

    def test_registration_login_and_authenticated_profile(self):
        headers, user = create_account(self.client, email="patient-a@example.com")
        self.assertEqual(user["role"], "patient")
        self.assertEqual(self.client.get("/api/auth/me", headers=headers).json()["email"], "patient-a@example.com")
        login = self.client.post("/api/auth/login", json={"email": "patient-a@example.com", "password": "valid-password-123"})
        self.assertEqual(login.status_code, 200)
        wrong = self.client.post("/api/auth/login", json={"email": "patient-a@example.com", "password": "wrong-password"})
        self.assertEqual(wrong.status_code, 401)

    def test_patient_cannot_access_another_journey_task(self):
        owner, _ = create_account(self.client, email="owner@example.com")
        other, _ = create_account(self.client, email="other@example.com")
        created = self.client.post("/api/tasks", headers=other, json={"title": "Private task", "category": "Other"})
        task_id = created.json()["id"]
        self.assertEqual(self.client.get("/api/tasks", headers=owner).json(), [])
        self.assertEqual(self.client.put(f"/api/tasks/{task_id}", headers=owner, json={"title": "Try to edit"}).status_code, 404)

    def test_caregiver_only_sees_assigned_tasks_and_cannot_edit_task_text(self):
        patient, _ = create_account(self.client, email="patient-share@example.com")
        invitation = self.client.post("/api/caregivers/invite", headers=patient, json={"email": "helper@example.com"}).json()
        caregiver, caregiver_user = create_account(self.client, role="caregiver", email="helper@example.com", invite_code=invitation["invitation_code"])
        task_a = self.client.post("/api/tasks", headers=patient, json={"title": "Collect report", "category": "Report Collection"}).json()
        task_b = self.client.post("/api/tasks", headers=patient, json={"title": "Private patient task", "category": "Other"}).json()
        assigned = self.client.post("/api/caregivers/assign-task", headers=patient, json={"task_id": task_a["id"], "caregiver_id": caregiver_user["id"]})
        self.assertEqual(assigned.status_code, 200)
        history = self.client.get(f"/api/tasks/{task_a['id']}/history", headers=patient).json()
        self.assertEqual(len(history["assignments"]), 1)
        self.assertTrue(history["assignments"][0]["active"])
        rows = self.client.get("/api/tasks", headers=caregiver).json()
        self.assertEqual([row["id"] for row in rows], [task_a["id"]])
        self.assertEqual(self.client.patch(f"/api/tasks/{task_a['id']}/status", headers=caregiver, json={"status": "Completed"}).status_code, 200)
        self.assertEqual(self.client.put(f"/api/tasks/{task_a['id']}", headers=caregiver, json={"title": "Altered instruction"}).status_code, 403)
        self.assertEqual(self.client.patch(f"/api/tasks/{task_b['id']}/status", headers=caregiver, json={"status": "Completed"}).status_code, 404)

    def test_upload_rejects_unsupported_and_spoofed_files(self):
        headers, _ = create_account(self.client, email="upload@example.com")
        unsupported = self.client.post("/api/documents/upload", headers=headers, files={"file": ("notes.txt", b"not a document", "text/plain")})
        spoofed = self.client.post("/api/documents/upload", headers=headers, files={"file": ("notes.pdf", b"not a pdf", "application/pdf")})
        self.assertEqual(unsupported.status_code, 415)
        self.assertEqual(spoofed.status_code, 415)

    def test_report_readiness_counts_only_verified_documents(self):
        headers, _ = create_account(self.client, email="reports@example.com")
        first = self.client.post("/api/reports", headers=headers, json={"name": "Blood test report", "status": "Missing"}).json()
        self.client.post("/api/reports", headers=headers, json={"name": "Discharge summary", "status": "Missing"})
        self.assertEqual(self.client.patch(f"/api/reports/{first['id']}", headers=headers, json={"status": "Verified"}).status_code, 400)
        uploaded = self.client.post("/api/documents/upload", headers=headers, files={"file": ("sample.pdf", b"%PDF-1.4 test file", "application/pdf")})
        self.assertEqual(uploaded.status_code, 201)
        attached = self.client.patch(f"/api/reports/{first['id']}", headers=headers, json={"status": "Verified", "document_id": uploaded.json()["id"]})
        self.assertEqual(attached.status_code, 200)
        readiness = self.client.get("/api/reports/readiness", headers=headers).json()
        self.assertEqual((readiness["available_count"], readiness["total_count"], readiness["readiness_percentage"]), (1, 2, 50))

    def test_dashboard_flags_overdue_administrative_task(self):
        headers, _ = create_account(self.client, email="dashboard@example.com")
        created = self.client.post("/api/tasks", headers=headers, json={"title": "Upload requested report", "category": "Report Collection",
                                  "due_date": (date.today() - timedelta(days=1)).isoformat()}).json()
        response = self.client.get("/api/dashboard", headers=headers)
        self.assertEqual(response.json()["summary"]["overdue_tasks"], 1)
        task = self.client.get("/api/tasks", headers=headers).json()[0]
        self.assertEqual((task["id"], task["status"]), (created["id"], "Overdue"))

    def test_notifications_are_private_to_the_recipient(self):
        first_headers, first_user = create_account(self.client, email="notified@example.com")
        second_headers, _ = create_account(self.client, email="not-other@example.com")
        db = SessionLocal()
        try:
            notification = Notification(user_id=first_user["id"], title="Private reminder", message="Check your report.")
            db.add(notification)
            db.commit()
            db.refresh(notification)
            notification_id = notification.id
        finally:
            db.close()
        self.assertEqual(len(self.client.get("/api/notifications", headers=first_headers).json()), 1)
        self.assertEqual(self.client.get("/api/notifications", headers=second_headers).json(), [])
        self.assertEqual(self.client.patch(f"/api/notifications/{notification_id}/read", headers=second_headers).status_code, 404)

    def test_no_key_analysis_is_explicitly_simulated(self):
        analysis, mode = analyze_document("A fictional discharge note with no verified instructions.")
        self.assertEqual(mode, "simulated")
        self.assertIn("simulated", analysis["simple_explanation"].lower())
        self.assertEqual(analysis["clinician_tasks"], [])

    def test_structured_document_analysis_requires_a_simple_explanation(self):
        with self.assertRaises(ValidationError):
            DocumentAnalysis.model_validate({"document_type": "Discharge summary"})

    def test_access_barrier_create_update_and_patient_scope(self):
        owner, _ = create_account(self.client, email="barrier-owner@example.com")
        other, _ = create_account(self.client, email="barrier-other@example.com")
        created = self.client.post("/api/barriers", headers=owner, json={"title": "Travel coordination", "category": "Travel difficulty"})
        self.assertEqual(created.status_code, 201)
        barrier_id = created.json()["id"]
        self.assertEqual(len(self.client.get("/api/barriers", headers=owner).json()), 1)
        self.assertEqual(self.client.get("/api/barriers", headers=other).json(), [])
        updated = self.client.put(f"/api/barriers/{barrier_id}", headers=owner, json={"status": "Resolved", "follow_up_notes": "Ride arranged."})
        self.assertEqual(updated.json()["status"], "Resolved")
        self.assertEqual(self.client.put(f"/api/barriers/{barrier_id}", headers=other, json={"status": "Resolved"}).status_code, 404)

    def test_fictional_demo_seed_has_requested_journey_content(self):
        db = SessionLocal()
        try:
            seed_demo(db)
        finally:
            db.close()
        login = self.client.post("/api/auth/login", json={"email": "demo@carebridge.ai", "password": "carebridge123"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        dashboard = self.client.get("/api/dashboard", headers=headers).json()
        self.assertEqual(dashboard["summary"]["total_tasks"], 5)
        self.assertEqual(dashboard["summary"]["required_reports"], 3)
        self.assertEqual(dashboard["summary"]["caregiver_count"], 2)
        self.assertEqual(dashboard["summary"]["overdue_tasks"], 1)
        self.assertEqual(len(dashboard["upcoming_appointments"]), 2)
        self.assertGreater(len(dashboard["recent_notifications"]), 0)

    def test_document_tasks_require_explicit_patient_confirmation(self):
        headers, user = create_account(self.client, email="document-review@example.com")
        db = SessionLocal()
        try:
            document = Document(patient_id=user["id"], filename="fictional-discharge.pdf", content_type="application/pdf",
                                storage_path="demo://sample", extracted_text="Fictional text for a patient-reviewed demo task.")
            db.add(document)
            db.commit()
            db.refresh(document)
            document_id = document.id
        finally:
            db.close()
        self.assertEqual(self.client.post(f"/api/documents/{document_id}/analyze", headers=headers, json={"consent": False}).status_code, 400)
        analyzed = self.client.post(f"/api/documents/{document_id}/analyze", headers=headers, json={"consent": True})
        self.assertEqual(analyzed.status_code, 200)
        self.assertEqual(analyzed.json()["analysis_mode"], "simulated")
        draft = {"title": "Review sample report", "description": "Patient-entered administrative reminder.",
                 "category": "Report Collection", "source_text": "Fictional text for a patient-reviewed demo task."}
        self.assertEqual(self.client.post(f"/api/documents/{document_id}/confirm", headers=headers,
                                          json={"confirmed": False, "tasks": [draft]}).status_code, 400)
        confirmed = self.client.post(f"/api/documents/{document_id}/confirm", headers=headers,
                                     json={"confirmed": True, "tasks": [draft]})
        self.assertEqual(confirmed.status_code, 200)
        task = self.client.get("/api/tasks", headers=headers).json()[0]
        self.assertEqual(task["status"], "Needs Verification")
        self.assertTrue(task["needs_clinician_verification"])


if __name__ == "__main__":
    unittest.main()
