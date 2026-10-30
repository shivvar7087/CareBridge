import json
from datetime import date, timedelta

from app.core.security import hash_password
from app.core.time import utc_now
from app.database.models import (AccessBarrier, CaregiverRelationship, Document, ExtractedDocumentData, HealthcareJourney,
                                 JourneyTask, Notification, PatientProfile, RequiredReport, TaskAssignment, User)

DEMO_EMAIL = "demo@carebridge.ai"
DEMO_PASSWORD = "carebridge123"


def seed_demo(db):
    if db.query(User).filter_by(email=DEMO_EMAIL).first():
        return
    patient = User(email=DEMO_EMAIL, full_name="Aarav Mehta", password_hash=hash_password(DEMO_PASSWORD), role="patient", is_demo=True)
    db.add(patient)
    db.flush()
    caregiver_one = User(email="priya.demo@carebridge.ai", full_name="Priya Mehta", password_hash=hash_password(DEMO_PASSWORD), role="caregiver", is_demo=True)
    caregiver_two = User(email="rohan.demo@carebridge.ai", full_name="Rohan Mehta", password_hash=hash_password(DEMO_PASSWORD), role="caregiver", is_demo=True)
    db.add_all([caregiver_one, caregiver_two])
    db.flush()
    db.add(PatientProfile(user_id=patient.id, preferred_language="English", hospital_name="Harborview Medical Centre"))
    db.add(HealthcareJourney(patient_id=patient.id))
    for caregiver in (caregiver_one, caregiver_two):
        db.add(CaregiverRelationship(patient_id=patient.id, caregiver_user_id=caregiver.id, invited_email=caregiver.email,
                                     invitation_code=f"demo-{caregiver.id}-carebridge", can_view_journey=True))

    today = date.today()
    appointment_date = today + timedelta(days=7)
    sample_text = (
        "FICTIONAL DEMO DISCHARGE SUMMARY\n"
        "Patient: Aarav Mehta (fictional)\n"
        "Hospital: Harborview Medical Centre\n"
        f"Discharge date: {today.strftime('%d %B %Y')}\n"
        "Follow-up: Attend the cardiology follow-up appointment on the date confirmed by the clinic.\n"
        "Diagnostic report: Upload the blood test report before your follow-up appointment.\n"
        "Medication information: See the attached clinician-approved medication list.\n"
        "This fictional sample is for product demonstration only."
    )
    document = Document(patient_id=patient.id, filename="demo-discharge-summary.txt", content_type="text/plain",
                        storage_path="demo://fictional-discharge-summary", extracted_text=sample_text,
                        document_type="Discharge summary", document_date=today.isoformat(), hospital_name="Harborview Medical Centre",
                        explanation="Fictional sample document for demonstration. Confirm care instructions with your clinician.",
                        analysis_mode="simulated", analyzed=True,
                        analysis_json=json.dumps({"document_type": "Discharge summary (fictional demo)", "document_date": today.isoformat(),
                                                  "hospital_name": "Harborview Medical Centre", "appointments": [],
                                                  "follow_up_instructions": ["Attend the cardiology follow-up appointment on the date confirmed by the clinic."],
                                                  "required_reports": ["Blood test report"], "clinician_tasks": [],
                                                  "medication_information": ["See the attached clinician-approved medication list."],
                                                  "administrative_instructions": ["Upload the blood test report before your follow-up appointment."],
                                                  "uncertain_fields": ["Follow-up appointment date"],
                                                  "simple_explanation": "Fictional sample for demonstration. Review the original document and confirm instructions with your care team."}))
    db.add(document)
    db.flush()
    db.add(ExtractedDocumentData(document_id=document.id, structured_json=document.analysis_json))
    tasks = [
        JourneyTask(patient_id=patient.id, title="Review discharge paperwork", description="Keep a copy of the clinician-approved discharge summary.", category="Hospital Discharge", status="Completed", completed_at=utc_now(), source_document_id=document.id),
        JourneyTask(patient_id=patient.id, title="Complete blood test", description="Administrative reminder from the fictional sample care plan.", category="Diagnostic Test", status="Completed", completed_at=utc_now(), source_document_id=document.id),
        JourneyTask(patient_id=patient.id, title="Upload blood test report", description="Attach the report for your care team to review.", category="Report Collection", status="Pending", due_date=today - timedelta(days=2), source_document_id=document.id, assigned_to_id=caregiver_one.id),
        JourneyTask(patient_id=patient.id, title="Cardiology follow-up appointment", description="Confirm the appointment date with the clinic.", category="Appointment", status="Scheduled", due_date=appointment_date, source_document_id=document.id),
        JourneyTask(patient_id=patient.id, title="Primary care follow-up appointment", description="Fictional demo appointment. Confirm any real appointment date with your clinic.", category="Appointment", status="Scheduled", due_date=today + timedelta(days=20), assigned_to_id=caregiver_two.id),
    ]
    db.add_all(tasks)
    db.flush()
    db.add_all([
        TaskAssignment(task_id=tasks[2].id, caregiver_user_id=caregiver_one.id, assigned_by_id=patient.id),
        TaskAssignment(task_id=tasks[4].id, caregiver_user_id=caregiver_two.id, assigned_by_id=patient.id),
    ])
    db.add_all([
        RequiredReport(patient_id=patient.id, name="Discharge summary", appointment_date=appointment_date, status="Verified", document_id=document.id),
        RequiredReport(patient_id=patient.id, name="Blood test report", appointment_date=appointment_date, status="Missing"),
        RequiredReport(patient_id=patient.id, name="Previous diagnostic report", appointment_date=appointment_date, status="Pending Upload"),
    ])
    db.add_all([
        Notification(user_id=patient.id, title="Report still needed", message="The blood test report is not marked as available yet.", kind="document"),
        Notification(user_id=patient.id, title="Upcoming appointment", message="Cardiology follow-up is scheduled in one week.", kind="appointment"),
        Notification(user_id=caregiver_one.id, title="Task assigned to you", message="Upload blood test report.", kind="task"),
    ])
    barrier = AccessBarrier(patient_id=patient.id, title="Travel planning", description="Coordinate transport for the upcoming appointment.", category="Travel difficulty", status="Open")
    db.add(barrier)
    db.commit()
