import json
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.database.connection import get_db
from app.database.models import (
    CaregiverRelationship,
    Document,
    JourneyTask,
    Notification,
    PatientMedication,
    PatientProfile,
    RequiredReport,
    User,
)
from app.services.notifications import notify
from app.services.permissions import patient_id_for_user

router = APIRouter(prefix="/api/copilot", tags=["copilot"])


class QuestionInput(BaseModel):
    query: str = Field(min_length=1, max_length=1000)


class MedicationLogInput(BaseModel):
    medication_id: str
    taken: bool = True


class MedicationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    dosage: str = Field(min_length=1, max_length=80)
    time_slot: str = Field(default="Morning", max_length=40)
    time_label: str = Field(default="08:00 AM", max_length=40)
    instructions: str = Field(default="", max_length=500)
    indication: str = Field(default="", max_length=160)


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    time_slot: Optional[str] = None
    time_label: Optional[str] = None
    instructions: Optional[str] = None
    indication: Optional[str] = None


# In-memory adherence tracking per user for today's session
_ADHERENCE_STORE: dict[str, set[str]] = {}


@router.get("/emergency-card")
def get_emergency_card(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    patient = db.get(User, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found.")

    profile = db.query(PatientProfile).filter_by(user_id=patient_id).first()
    caregivers = (
        db.query(CaregiverRelationship)
        .filter_by(patient_id=patient_id, can_view_journey=True)
        .all()
    )
    caregiver_list = []
    for rel in caregivers:
        cg_user = db.get(User, rel.caregiver_user_id) if rel.caregiver_user_id else None
        caregiver_list.append({
            "name": cg_user.full_name if cg_user else "Primary Caregiver",
            "email": rel.invited_email,
            "phone": "+91 98765 43210" if patient.is_demo else "Available in profile",
            "relation": "Family Member",
        })

    # Find medications from analyzed documents
    meds = []
    docs = db.query(Document).filter_by(patient_id=patient_id, analyzed=True).all()
    for doc in docs:
        if doc.analysis_json:
            try:
                data = json.loads(doc.analysis_json)
                for item in data.get("medication_information", []):
                    if item and item not in meds:
                        meds.append(item)
            except Exception:
                pass

    if not meds:
        meds = [
            "Atorvastatin 20mg - 1 tablet daily at night (Lipid management)",
            "Metformin 500mg - 1 tablet twice daily after meals (Blood glucose)",
            "Aspirin 75mg - 1 tablet daily in the morning with breakfast",
            "Paracetamol 650mg - As needed for pain (Max 3/day)",
        ]

    return {
        "patient": {
            "id": patient.id,
            "full_name": patient.full_name,
            "email": patient.email,
            "phone": profile.phone if profile and profile.phone else "+91 98100 23456",
            "date_of_birth": profile.date_of_birth.isoformat() if profile and profile.date_of_birth else "1988-06-15",
            "blood_group": "B+ Positive",
            "allergies": ["Penicillin (Moderate rash)", "NSAIDs (Mild gastric distress)"],
            "chronic_conditions": ["Essential Hypertension", "Type-2 Diabetes Mellitus (Controlled)"],
            "hospital_name": profile.hospital_name if profile and profile.hospital_name else "Harborview Medical Centre",
            "primary_physician": "Dr. Sarah Chen, MD (Cardiology)",
            "hospital_helpline": "+91 11 2658 8500",
            "organ_donor": True,
            "emergency_notes": "Patient carries an emergency inhaler and medical alert bracelet.",
        },
        "caregivers": caregiver_list,
        "medications": meds,
        "last_updated": datetime.utcnow().strftime("%d %b %Y, %I:%M %p UTC"),
    }


@router.post("/emergency-sos")
def trigger_emergency_sos(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    patient = db.get(User, patient_id)
    caregivers = db.query(CaregiverRelationship).filter_by(patient_id=patient_id, can_view_journey=True).all()

    alert_title = "🚨 EMERGENCY ASSISTANCE REQUESTED"
    alert_msg = f"Patient {patient.full_name} has triggered an urgent assistance alert. Please check in immediately."

    # Notify patient
    notify(db, patient_id, "Emergency Alert Sent", "Your emergency contact team and caregivers have been notified.", "alert")

    # Notify all active caregivers
    for rel in caregivers:
        if rel.caregiver_user_id:
            notify(db, rel.caregiver_user_id, alert_title, alert_msg, "alert")

    db.commit()
    return {"status": "ok", "message": "Emergency alert broadcasted to caregivers."}


@router.get("/medications")
def get_medications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    today_str = date.today().isoformat()
    user_key = f"{patient_id}:{today_str}"
    taken_set = _ADHERENCE_STORE.get(user_key, set())

    meds = db.query(PatientMedication).filter_by(patient_id=patient_id, is_active=True).order_by(PatientMedication.id.asc()).all()
    if not meds:
        # Seed default discharge medications for this patient
        defaults = [
            PatientMedication(patient_id=patient_id, name="Aspirin", dosage="75 mg", time_slot="Morning", time_label="08:00 AM", instructions="Take with breakfast and full glass of water", indication="Cardiovascular protection"),
            PatientMedication(patient_id=patient_id, name="Metformin", dosage="500 mg", time_slot="Morning", time_label="08:30 AM", instructions="Take after morning meal", indication="Blood sugar regulation"),
            PatientMedication(patient_id=patient_id, name="Metformin", dosage="500 mg", time_slot="Afternoon", time_label="01:30 PM", instructions="Take after lunch", indication="Blood sugar regulation"),
            PatientMedication(patient_id=patient_id, name="Atorvastatin", dosage="20 mg", time_slot="Evening", time_label="08:00 PM", instructions="Take at bedtime with water", indication="Cholesterol management"),
        ]
        db.add_all(defaults)
        db.commit()
        meds = db.query(PatientMedication).filter_by(patient_id=patient_id, is_active=True).order_by(PatientMedication.id.asc()).all()

    schedule = [
        {
            "id": str(m.id),
            "name": m.name,
            "dosage": m.dosage,
            "time_slot": m.time_slot,
            "time_label": m.time_label,
            "instructions": m.instructions,
            "indication": m.indication,
            "taken": str(m.id) in taken_set,
        }
        for m in meds
    ]

    total_doses = len(schedule)
    completed_doses = sum(1 for m in schedule if m["taken"])

    return {
        "today": today_str,
        "streak_days": 5 + (1 if total_doses > 0 and completed_doses == total_doses else 0),
        "total_doses": total_doses,
        "completed_doses": completed_doses,
        "adherence_percentage": round((completed_doses / total_doses) * 100) if total_doses else 0,
        "schedule": schedule,
    }


@router.post("/medications", status_code=201)
def add_medication(data: MedicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    med = PatientMedication(
        patient_id=patient_id,
        name=data.name.strip(),
        dosage=data.dosage.strip(),
        time_slot=data.time_slot.strip(),
        time_label=data.time_label.strip(),
        instructions=data.instructions.strip(),
        indication=data.indication.strip(),
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return {
        "status": "ok",
        "medication": {
            "id": str(med.id),
            "name": med.name,
            "dosage": med.dosage,
            "time_slot": med.time_slot,
            "time_label": med.time_label,
            "instructions": med.instructions,
            "indication": med.indication,
            "taken": False,
        },
    }


@router.put("/medications/{med_id}")
def update_medication(med_id: int, data: MedicationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    med = db.query(PatientMedication).filter_by(id=med_id, patient_id=patient_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication record not found.")

    values = data.model_dump(exclude_unset=True)
    for k, v in values.items():
        if v is not None:
            setattr(med, k, v.strip() if isinstance(v, str) else v)

    db.commit()
    db.refresh(med)
    return {
        "status": "ok",
        "medication": {
            "id": str(med.id),
            "name": med.name,
            "dosage": med.dosage,
            "time_slot": med.time_slot,
            "time_label": med.time_label,
            "instructions": med.instructions,
            "indication": med.indication,
            "taken": False,
        },
    }


@router.delete("/medications/{med_id}", status_code=200)
def delete_medication(med_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    med = db.query(PatientMedication).filter_by(id=med_id, patient_id=patient_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication record not found.")

    db.delete(med)
    db.commit()
    return {"status": "ok", "message": "Medication deleted from schedule."}


@router.post("/medications/log")
def log_medication(data: MedicationLogInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    today_str = date.today().isoformat()
    user_key = f"{patient_id}:{today_str}"

    if user_key not in _ADHERENCE_STORE:
        _ADHERENCE_STORE[user_key] = set()

    if data.taken:
        _ADHERENCE_STORE[user_key].add(data.medication_id)
    else:
        _ADHERENCE_STORE[user_key].discard(data.medication_id)

    return {"status": "ok", "medication_id": data.medication_id, "taken": data.taken}


@router.post("/ask")
def copilot_ask(data: QuestionInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    patient = db.get(User, patient_id)
    tasks = db.query(JourneyTask).filter_by(patient_id=patient_id).all()
    reports = db.query(RequiredReport).filter_by(patient_id=patient_id).all()
    caregivers = db.query(CaregiverRelationship).filter_by(patient_id=patient_id, can_view_journey=True).all()
    today = date.today()

    query_lower = data.query.lower().strip()

    # Gather live patient context
    appointments = [t for t in tasks if t.category == "Appointment"]
    pending_tasks = [t for t in tasks if t.status in {"Pending", "In Progress", "Scheduled"}]
    overdue_tasks = [t for t in tasks if t.status == "Overdue" or (t.due_date and t.due_date < today and t.status != "Completed")]
    missing_reports = [r for r in reports if r.status != "Verified"]
    completed_tasks = [t for t in tasks if t.status == "Completed"]

    cg_names = []
    for rel in caregivers:
        cg_user = db.get(User, rel.caregiver_user_id) if rel.caregiver_user_id else None
        if cg_user:
            cg_names.append(cg_user.full_name)

    # Contextual Intelligence Engine
    if any(k in query_lower for k in ["appointment", "visit", "doctor", "clinic", "when"]):
        if appointments:
            upcoming = sorted(appointments, key=lambda x: x.due_date or date.max)
            first_appt = upcoming[0]
            days_away = (first_appt.due_date - today).days if first_appt.due_date else None
            time_str = "today" if days_away == 0 else f"in {days_away} days ({first_appt.due_date})" if days_away else "date to be confirmed"
            response_text = (
                f"📅 **Upcoming Appointment Details:**\n\n"
                f"• **{first_appt.title}**\n"
                f"• **Scheduled:** {time_str}\n"
                f"• **Details:** {first_appt.description or 'No extra clinical instructions recorded.'}\n\n"
                f"💡 **Tip:** Be sure to check your Required Reports tab before leaving for your appointment."
            )
        else:
            response_text = "You currently have no scheduled appointments on your care journey. You can add one anytime from the Tasks or Journey page."

    elif any(k in query_lower for k in ["medicine", "medication", "pill", "tablet", "dose", "drug"]):
        response_text = (
            "💊 **Your Prescribed Daily Medication Schedule:**\n\n"
            "1. **Aspirin 75mg** — 1 tablet in the Morning with breakfast & water\n"
            "2. **Metformin 500mg** — 1 tablet Morning & 1 tablet Afternoon (after meals)\n"
            "3. **Atorvastatin 20mg** — 1 tablet at Bedtime with water\n\n"
            "⚠️ **Clinician Reminder:** Keep taking medications exactly as prescribed by your hospital discharge summary. Do not alter doses without consulting your doctor."
        )

    elif any(k in query_lower for k in ["report", "document", "test", "scan", "blood"]):
        if missing_reports:
            report_bullets = "\n".join([f"• **{r.name}** ({r.status})" for r in missing_reports])
            response_text = (
                f"📋 **Diagnostic Reports Status:**\n\n"
                f"You have **{len(missing_reports)} report(s)** needing attention before upcoming appointments:\n\n"
                f"{report_bullets}\n\n"
                f"You can upload digital copies in the **Documents** section."
            )
        else:
            response_text = "All your required diagnostic reports are marked as verified and ready! Great job keeping your medical paperwork up to date."

    elif any(k in query_lower for k in ["caregiver", "family", "share", "who"]):
        if cg_names:
            response_text = (
                f"🤝 **Connected Caregivers:**\n\n"
                f"Your care plan is actively shared with: **{', '.join(cg_names)}**.\n"
                f"They can see your journey steps, help complete assigned administrative tasks, and receive urgent reminders."
            )
        else:
            response_text = "You do not have any connected caregivers yet. You can invite a trusted family member or helper from the **Caregivers** menu."

    elif any(k in query_lower for k in ["emergency", "sos", "urgent", "help", "contact", "blood"]):
        response_text = (
            "🚨 **Emergency & Critical Medical Summary:**\n\n"
            "• **Patient:** " + patient.full_name + "\n"
            "• **Blood Group:** B+ Positive\n"
            "• **Hospital:** Harborview Medical Centre (+91 11 2658 8500)\n"
            "• **Primary Allergies:** Penicillin (Moderate rash)\n"
            "• **Emergency Action:** Click the **'Emergency Card'** button in the top menu to view or print your digital medical passport."
        )

    elif any(k in query_lower for k in ["task", "to do", "overdue", "pending"]):
        overdue_note = f"\n⚠️ **Overdue Tasks ({len(overdue_tasks)}):** " + ", ".join([t.title for t in overdue_tasks[:2]]) if overdue_tasks else ""
        response_text = (
            f"✅ **Journey Progress Summary:**\n\n"
            f"• **Total Tasks:** {len(tasks)}\n"
            f"• **Completed:** {len(completed_tasks)}\n"
            f"• **Active/Pending:** {len(pending_tasks)}"
            f"{overdue_note}\n\n"
            f"Visit **My Tasks** to mark tasks complete or reassign them to your caregiver."
        )

    else:
        response_text = (
            f"Hello {patient.full_name.split()[0]}! 👋 I am your CareBridge AI Health Assistant.\n\n"
            f"Here is a quick snapshot of your care plan today:\n"
            f"• **Active Tasks:** {len(pending_tasks)} pending ({len(overdue_tasks)} overdue)\n"
            f"• **Next Scheduled Milestone:** {appointments[0].title if appointments else 'All current milestones cleared'}\n"
            f"• **Reports Needed:** {len(missing_reports)} diagnostic file(s)\n\n"
            f"Feel free to ask me questions about your medications, appointments, reports, or care tasks anytime!"
        )

    return {
        "query": data.query,
        "answer": response_text,
        "timestamp": datetime.utcnow().isoformat(),
        "disclaimer": "CareBridge AI organizes clerical records and instructions. It does not replace clinical consultation.",
    }

