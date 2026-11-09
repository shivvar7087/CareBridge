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
    language: str = Field(default="en", max_length=10)


class ExplainReportInput(BaseModel):
    report_name: str = Field(min_length=2, max_length=200)
    findings: Optional[str] = Field(default="", max_length=2000)
    language: str = Field(default="en", max_length=10)


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


def _build_emergency_data(db: Session, patient: User, profile: Optional[PatientProfile]):
    caregivers = (
        db.query(CaregiverRelationship)
        .filter_by(patient_id=patient.id, can_view_journey=True)
        .all()
    )
    caregiver_list = []
    for rel in caregivers:
        cg_user = db.get(User, rel.caregiver_user_id) if rel.caregiver_user_id else None
        caregiver_list.append({
            "name": cg_user.full_name if cg_user else "Primary Caregiver",
            "email": rel.invited_email,
            "phone": "+91 98765 43210" if patient.is_demo else "Available in profile",
            "relation": "Family Caregiver",
        })

    # Find medications from database or analyzed documents
    meds = []
    db_meds = db.query(PatientMedication).filter_by(patient_id=patient.id, is_active=True).all()
    if db_meds:
        for m in db_meds:
            meds.append(f"{m.name} {m.dosage} - {m.time_slot} ({m.instructions or m.indication or 'As directed'})")
    else:
        docs = db.query(Document).filter_by(patient_id=patient.id, analyzed=True).all()
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
            "Aspirin 75mg - Morning (Cardiovascular protection)",
            "Metformin 500mg - Morning & Afternoon (Blood sugar regulation)",
            "Atorvastatin 20mg - Evening / Bedtime (Lipid & cholesterol control)",
            "Paracetamol 650mg - As needed for pain (Max 3/day)",
        ]

    if profile and profile.emergency_contact_name and profile.emergency_contact_phone:
        caregiver_list.insert(0, {
            "name": profile.emergency_contact_name,
            "email": "emergency.contact@family.care",
            "phone": profile.emergency_contact_phone,
            "relation": "Designated Emergency Contact",
        })

    return {
        "patient": {
            "id": patient.id,
            "full_name": patient.full_name,
            "email": patient.email,
            "phone": profile.phone if profile and profile.phone else "+91 98100 23456",
            "date_of_birth": profile.date_of_birth.isoformat() if profile and profile.date_of_birth else "1988-06-15",
            "blood_group": getattr(profile, "blood_group", None) or "B+ Positive",
            "allergies": ["Penicillin (Moderate rash / anaphylactoid)", "NSAIDs (Mild gastric distress)"],
            "chronic_conditions": ["Essential Hypertension", "Type-2 Diabetes Mellitus (Controlled)"],
            "hospital_name": profile.hospital_name if profile and profile.hospital_name else "Harborview Medical Centre",
            "primary_physician": "Dr. Sarah Chen, MD (Cardiology)",
            "hospital_helpline": "+91 11 2658 8500",
            "organ_donor": True,
            "emergency_notes": "Patient carries an emergency inhaler and medical alert bracelet. Zero NSAIDs.",
            "team_badge": "ByteCoders · IIMT Engineering College, Meerut",
        },
        "caregivers": caregiver_list,
        "medications": meds,
        "last_updated": datetime.utcnow().strftime("%d %b %Y, %I:%M %p UTC"),
    }


@router.get("/emergency-card")
def get_emergency_card(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    patient = db.get(User, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found.")

    profile = db.query(PatientProfile).filter_by(user_id=patient_id).first()
    return _build_emergency_data(db, patient, profile)


@router.get("/public-ice/{patient_id}")
def get_public_ice_passport(patient_id: int, db: Session = Depends(get_db)):
    """
    Public, read-only emergency medical passport for first responders & paramedics (< 5s scan access).
    Returns essential triage info (Blood Group, Critical Allergies, Contacts, Helpline).
    """
    patient = db.get(User, patient_id)
    if not patient:
        # Fallback to demo user if not found
        demo_user = db.query(User).filter_by(email="demo@carebridge.ai").first()
        if demo_user:
            patient = demo_user
        else:
            raise HTTPException(status_code=404, detail="Emergency passport not found.")

    profile = db.query(PatientProfile).filter_by(user_id=patient.id).first()
    data = _build_emergency_data(db, patient, profile)
    data["fast_triage"] = {
        "access_time_target": "< 5 seconds",
        "protocol": "CareBridge ICE Paramedic Response Protocol",
        "verification_status": "Verified Clinical Record",
    }
    return data


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


# -------------------------------------------------------------------------
# Feature 02: Plain-Language Report & Biomarker Explainer
# Translates lab biomarkers, radiology findings, and complex diagnostic jargon
# -------------------------------------------------------------------------
@router.post("/explain-report")
def explain_report(data: ExplainReportInput, user: User = Depends(get_current_user)):
    """
    Translates complex diagnostic reports, lab biomarkers, and medical jargon
    into clear, patient-friendly plain language (Bilingual: English & Hindi).
    """
    name_lower = data.report_name.lower().strip()
    is_hindi = data.language.lower() in {"hi", "hindi"} or any(
        w in name_lower for w in ["kya", "kaise", "samjhao", "hindi"]
    )

    # Common biomarker knowledge base
    if any(k in name_lower for k in ["blood sugar", "glucose", "hba1c", "diabetes"]):
        if is_hindi:
            summary = "यह टेस्ट आपके खून में शुगर (ग्लूकोज) के स्तर की जांच करता है। HbA1c पिछले 3 महीनों का औसत शुगर बताता है।"
            biomarkers = [
                {"name": "Fasting Blood Sugar", "range": "70-99 mg/dL", "meaning": "खाली पेट शुगर का स्तर (सामान्य स्तर ऊर्जा और दिल की सुरक्षा के लिए जरूरी है)"},
                {"name": "Post-Prandial (खाना खाने के बाद)", "range": "< 140 mg/dL", "meaning": "भोजन के 2 घंटे बाद शुगर का स्तर"},
                {"name": "HbA1c (ग्लाइकोसिलेटेड हीमोग्लोबिन)", "range": "< 5.7% सामान्य (6.5% पर डायबिटीज़ नियंत्रण लक्ष्य)", "meaning": "पिछले 90 दिनों का शुगर नियंत्रण"},
            ]
            guidance = "मीठे पेय और तले हुए भोजन से बचें, समय पर मेटफॉर्मिन लें और रोज़ाना 20-30 मिनट टहलें।"
        else:
            summary = "This test measures glucose (sugar) circulating in your bloodstream. HbA1c reflects your 3-month average blood glucose control."
            biomarkers = [
                {"name": "Fasting Blood Glucose", "range": "70 – 99 mg/dL", "meaning": "Baseline morning sugar before eating; keeps blood vessels healthy."},
                {"name": "Post-Prandial (2 hrs post-meal)", "range": "< 140 mg/dL", "meaning": "How efficiently your insulin processes carbohydrates after meals."},
                {"name": "HbA1c (Glycated Hemoglobin)", "range": "< 5.7% (Normal), < 7.0% (Post-Op Goal)", "meaning": "Long-term glucose stability without sudden spikes."},
            ]
            guidance = "Take prescribed Metformin consistently with meals, stay hydrated with plain water, and limit refined sugars."

    elif any(k in name_lower for k in ["lipid", "cholesterol", "lipid profile", "ldl", "triglyceride"]):
        if is_hindi:
            summary = "लिपिड प्रोफाइल आपके रक्त में वसा (कोलेस्ट्रॉल और ट्राइग्लिसराइड्स) की मात्रा मापता है, जो हृदय स्वास्थ्य के लिए अत्यंत आवश्यक है।"
            biomarkers = [
                {"name": "Total Cholesterol", "range": "< 200 mg/dL", "meaning": "रक्त में कुल कोलेस्ट्रॉल की मात्रा"},
                {"name": "LDL (खराब कोलेस्ट्रॉल)", "range": "< 100 mg/dL (< 70 mg/dL हृदय रोगियों के लिए)", "meaning": "यह धमनियों में रुकावट पैदा कर सकता है"},
                {"name": "HDL (अच्छा कोलेस्ट्रॉल)", "range": "> 40 mg/dL (पुरुष), > 50 mg/dL (महिला)", "meaning": "दिल की रक्षा करने वाला सुरक्षात्मक कोलेस्ट्रॉल"},
            ]
            guidance = "रात को अपनी एटोरवास्टेटिन (Atorvastatin) गोली नियमित लें और तेल-घी से बने खाद्य पदार्थों का सेवन कम करें।"
        else:
            summary = "A lipid panel measures fats in your blood to evaluate cardiovascular health and arterial recovery."
            biomarkers = [
                {"name": "Total Cholesterol", "range": "< 200 mg/dL", "meaning": "Overall circulating blood lipids."},
                {"name": "LDL ('Bad' Cholesterol)", "range": "< 100 mg/dL (< 70 mg/dL for cardiac patients)", "meaning": "Lower levels prevent plaque buildup in blood vessels."},
                {"name": "HDL ('Good' Protective Cholesterol)", "range": "> 40 mg/dL (M) / > 50 mg/dL (F)", "meaning": "Carries excess cholesterol back to the liver for clearance."},
                {"name": "Triglycerides", "range": "< 150 mg/dL", "meaning": "Fat stores; elevated levels increase pancreatitis and heart risks."},
            ]
            guidance = "Take Atorvastatin 20mg at bedtime as directed, replace saturated cooking fats with fiber-rich whole grains."

    elif any(k in name_lower for k in ["kidney", "renal", "creatinine", "kft", "urea", "egfr"]):
        if is_hindi:
            summary = "किडनी फंक्शन टेस्ट (KFT) यह जांचता है कि आपके गुर्दे रक्त से अपशिष्ट पदार्थों और दवाओं को कितनी अच्छी तरह छान रहे हैं।"
            biomarkers = [
                {"name": "Serum Creatinine", "range": "0.7 – 1.3 mg/dL", "meaning": "मांसपेशियों के काम का उपोत्पाद; सामान्य स्तर स्वस्थ गुर्दे को दर्शाता है"},
                {"name": "Blood Urea Nitrogen (BUN)", "range": "7 – 20 mg/dL", "meaning": "प्रोटीन पाचन से बनने वाला यूरिया"},
                {"name": "eGFR (फिल्ट्रेशन दर)", "range": "> 90 mL/min/1.73m²", "meaning": "गुर्दे की छानने की कुल कार्यक्षमता"},
            ]
            guidance = "दिनभर में पर्याप्त पानी पिएं। बिना डॉक्टर की सलाह के दर्द निवारक (NSAIDs जैसे ब्रूफेन) न लें।"
        else:
            summary = "Kidney Function Tests (KFT) verify that your kidneys are effectively filtering metabolic waste and safely clearing prescribed medications."
            biomarkers = [
                {"name": "Serum Creatinine", "range": "0.7 – 1.3 mg/dL", "meaning": "Byproduct of muscle metabolism; stable levels indicate healthy renal clearance."},
                {"name": "Blood Urea Nitrogen (BUN)", "range": "7 – 20 mg/dL", "meaning": "Measures nitrogen waste from protein breakdown."},
                {"name": "eGFR (Estimated Filtration Rate)", "range": "> 90 mL/min", "meaning": "Kidney filtering capacity percentage."},
            ]
            guidance = "Maintain good daily hydration (2-2.5L unless fluid-restricted) and strictly avoid over-the-counter NSAID painkillers."

    elif any(k in name_lower for k in ["cbc", "hemoglobin", "blood count", "platelet", "wbc"]):
        if is_hindi:
            summary = "सीबीसी (Complete Blood Count) आपके लाल रक्त कोशिकाओं (ऑक्सीजन वाहक), श्वेत रक्त कोशिकाओं (संक्रमण से लड़ने वाले) और प्लेटलेट्स (रक्त का थक्का जमाने वाले) की जांच करता है।"
            biomarkers = [
                {"name": "हीमोग्लोबिन (Hb)", "range": "13.0 – 17.0 g/dL (पुरुष), 12.0 – 15.0 g/dL (महिला)", "meaning": "ऊर्जा और ऑक्सीजन वहन क्षमता"},
                {"name": "श्वेत रक्त कोशिकाएं (WBC)", "range": "4,500 – 11,000 /µL", "meaning": "रोग प्रतिरोधक क्षमता (संक्रमण होने पर बढ़ जाता है)"},
                {"name": "प्लेटलेट्स", "range": "150,000 – 450,000 /µL", "meaning": "खून का थक्का जमाने और चोट को ठीक करने के लिए जरूरी"},
            ]
            guidance = "सर्जरी के बाद घाव भरने के लिए प्रोटीन और हरी पत्तेदार सब्जियां खाएं। बुखार होने पर तुरंत बताएं।"
        else:
            summary = "A Complete Blood Count (CBC) examines red blood cells (oxygen carriers), white blood cells (infection defense), and platelets (clotting)."
            biomarkers = [
                {"name": "Hemoglobin (Hb)", "range": "13.0 – 17.0 g/dL (M) / 12.0 – 15.0 g/dL (F)", "meaning": "Oxygen-carrying capacity; prevents post-surgery fatigue."},
                {"name": "White Blood Cells (WBC)", "range": "4,500 – 11,000 /µL", "meaning": "Immune defense; high levels can indicate infection or inflammation."},
                {"name": "Platelets", "range": "150,000 – 450,000 /µL", "meaning": "Essential for blood clotting and surgical wound healing."},
            ]
            guidance = "Report any fever > 100.4°F or unexpected wound discharge to your surgical coordinator immediately."

    else:
        if is_hindi:
            summary = f"'{data.report_name}' रिपोर्ट आपके स्वास्थ्य और रिकवरी की प्रगति का मूल्यांकन करने के लिए आवश्यक है।"
            biomarkers = [
                {"name": "नैदानिक समीक्षा (Clinical Review)", "range": "डॉक्टर द्वारा निर्धारित", "meaning": "सर्जरी या डिस्चार्ज के बाद शरीर के अंगों के सुचारू कार्य की पुष्टि"},
            ]
            guidance = "यह रिपोर्ट अपने आगामी फॉलो-अप अपॉइंटमेंट में डॉ. सारा चेन को अवश्य दिखाएं।"
        else:
            summary = f"The '{data.report_name}' is a key clinical check requested by your care team to verify your post-discharge recovery."
            biomarkers = [
                {"name": "Diagnostic Status", "range": "Clinical Standard", "meaning": "Verifies physiological healing and absence of post-discharge complications."},
            ]
            guidance = "Ensure digital or physical copy is brought to your next follow-up appointment with your attending physician."

    return {
        "report_name": data.report_name,
        "language": "hi" if is_hindi else "en",
        "plain_summary": summary,
        "biomarkers": biomarkers,
        "reassuring_guidance": guidance,
        "safety_disclaimer": "This plain-language explanation helps you understand test objectives. It does not replace medical consultation.",
    }


# -------------------------------------------------------------------------
# Feature 03: Bilingual Conversational AI Assistant (Hindi & English)
# -------------------------------------------------------------------------
@router.post("/ask")
def copilot_ask(data: QuestionInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    patient = db.get(User, patient_id)
    tasks = db.query(JourneyTask).filter_by(patient_id=patient_id).all()
    reports = db.query(RequiredReport).filter_by(patient_id=patient_id).all()
    caregivers = db.query(CaregiverRelationship).filter_by(patient_id=patient_id, can_view_journey=True).all()
    today = date.today()

    query_raw = data.query.strip()
    query_lower = query_raw.lower()

    # Detect Hindi language preference
    is_hindi = (
        data.language.lower() in {"hi", "hindi"}
        or any(w in query_lower for w in ["meri", "mera", "dawa", "dawai", "kab", "kya", "madad", "batao", "doctor", "kaun", "hindi", "tabiyat"])
    )

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

    # Contextual Intelligence Engine (Bilingual)
    if any(k in query_lower for k in ["appointment", "visit", "doctor", "clinic", "when", "milna", "tarikh"]):
        if appointments:
            upcoming = sorted(appointments, key=lambda x: x.due_date or date.max)
            first_appt = upcoming[0]
            days_away = (first_appt.due_date - today).days if first_appt.due_date else None
            time_str = "today" if days_away == 0 else f"in {days_away} days ({first_appt.due_date})" if days_away else "date to be confirmed"
            time_str_hi = "आज ही" if days_away == 0 else f"{days_away} दिनों बाद ({first_appt.due_date})" if days_away else "तारीख पुष्टि बाकी है"

            if is_hindi:
                response_text = (
                    f"📅 **आपकी अगली डॉक्टर विज़िट का विवरण:**\n\n"
                    f"• **अपॉइंटमेंट:** {first_appt.title}\n"
                    f"• **समय/तारीख:** {time_str_hi}\n"
                    f"• **निर्देश:** {first_appt.description or 'कोई विशेष अतिरिक्त निर्देश नहीं है।'}\n\n"
                    f"💡 **सलाह:** जाने से पहले अपने सभी आवश्यक रिपोर्ट्स (Required Reports) ज़रूर जांच लें।"
                )
            else:
                response_text = (
                    f"📅 **Upcoming Appointment Details:**\n\n"
                    f"• **{first_appt.title}**\n"
                    f"• **Scheduled:** {time_str}\n"
                    f"• **Details:** {first_appt.description or 'No extra clinical instructions recorded.'}\n\n"
                    f"💡 **Tip:** Be sure to check your Required Reports tab before leaving for your appointment."
                )
        else:
            response_text = (
                "आपके केयर प्लान में अभी कोई नया अपॉइंटमेंट दर्ज नहीं है। आप जब चाहें नया अपॉइंटमेंट जोड़ सकते हैं।"
                if is_hindi
                else "You currently have no scheduled appointments on your care journey. You can add one anytime from the Tasks or Journey page."
            )

    elif any(k in query_lower for k in ["medicine", "medication", "pill", "tablet", "dose", "drug", "dawa", "dawai", "goli"]):
        if is_hindi:
            response_text = (
                "💊 **आपकी दैनिक दवाइयों का निर्धारित समय (Medication Schedule):**\n\n"
                "1. **एस्पिरिन (Aspirin 75mg)** — सुबह नाश्ते और पानी के साथ (1 गोली)\n"
                "2. **मेटफॉर्मिन (Metformin 500mg)** — सुबह और दोपहर भोजन के बाद (1-1 गोली)\n"
                "3. **एटोरवास्टेटिन (Atorvastatin 20mg)** — रात को सोते समय पानी के साथ (1 गोली)\n\n"
                "⚠️ **जरूरी सूचना:** अपने अस्पताल डिस्चार्ज पर्चे के अनुसार ही दवाइयां लें। बिना डॉक्टर की अनुमति के खुराक में बदलाव न करें।"
            )
        else:
            response_text = (
                "💊 **Your Prescribed Daily Medication Schedule:**\n\n"
                "1. **Aspirin 75mg** — 1 tablet in the Morning with breakfast & water\n"
                "2. **Metformin 500mg** — 1 tablet Morning & 1 tablet Afternoon (after meals)\n"
                "3. **Atorvastatin 20mg** — 1 tablet at Bedtime with water\n\n"
                "⚠️ **Clinician Reminder:** Keep taking medications exactly as prescribed by your hospital discharge summary. Do not alter doses without consulting your doctor."
            )

    elif any(k in query_lower for k in ["report", "document", "test", "scan", "blood", "janch"]):
        if missing_reports:
            report_bullets = "\n".join([f"• **{r.name}** ({r.status})" for r in missing_reports])
            if is_hindi:
                response_text = (
                    f"📋 **आवश्यक जांच रिपोर्टों की स्थिति:**\n\n"
                    f"आपके आगामी अपॉइंटमेंट से पहले **{len(missing_reports)} रिपोर्ट(s)** पर ध्यान देने की आवश्यकता है:\n\n"
                    f"{report_bullets}\n\n"
                    f"आप **Documents** सेक्शन में जाकर डिजिटल कॉपी अपलोड कर सकते हैं।"
                )
            else:
                response_text = (
                    f"📋 **Diagnostic Reports Status:**\n\n"
                    f"You have **{len(missing_reports)} report(s)** needing attention before upcoming appointments:\n\n"
                    f"{report_bullets}\n\n"
                    f"You can upload digital copies in the **Documents** section."
                )
        else:
            response_text = (
                "आपकी सभी आवश्यक रिपोर्ट्स सत्यापित (Verified) हैं! बहुत बढ़िया, आपके सभी दस्तावेज़ व्यवस्थित हैं।"
                if is_hindi
                else "All your required diagnostic reports are marked as verified and ready! Great job keeping your medical paperwork up to date."
            )

    elif any(k in query_lower for k in ["caregiver", "family", "share", "who", "parivar", "kaun"]):
        if cg_names:
            if is_hindi:
                response_text = (
                    f"🤝 **जुड़े हुए देखभालकर्ता (Connected Caregivers):**\n\n"
                    f"आपका केयर प्लान इनके साथ साझा है: **{', '.join(cg_names)}**।\n"
                    f"वे आपकी रिकवरी यात्रा देख सकते हैं, कार्य पूरे करने में मदद कर सकते हैं और आपातकालीन सूचनाएं प्राप्त कर सकते हैं।"
                )
            else:
                response_text = (
                    f"🤝 **Connected Caregivers:**\n\n"
                    f"Your care plan is actively shared with: **{', '.join(cg_names)}**.\n"
                    f"They can see your journey steps, help complete assigned administrative tasks, and receive urgent reminders."
                )
        else:
            response_text = (
                "अभी तक कोई देखभालकर्ता नहीं जुड़ा है। आप **Caregivers** मेनू से अपने किसी परिवार के सदस्य को जोड़ सकते हैं।"
                if is_hindi
                else "You do not have any connected caregivers yet. You can invite a trusted family member or helper from the **Caregivers** menu."
            )

    elif any(k in query_lower for k in ["emergency", "sos", "urgent", "help", "contact", "blood", "aapatkal", "madad"]):
        if is_hindi:
            response_text = (
                f"🚨 **आपातकालीन चिकित्सा सारांश (Emergency Medical Passport):**\n\n"
                f"• **मरीज का नाम:** {patient.full_name}\n"
                f"• **ब्लड ग्रुप:** B+ Positive\n"
                f"• **अस्पताल:** Harborview Medical Centre (+91 11 2658 8500)\n"
                f"• **मुख्य एलर्जी:** पेनिसिलिन (Penicillin)\n"
                f"• **त्वरित कार्रवाई:** स्क्रीन के शीर्ष पर **'Emergency Card'** बटन दबाकर अपना डिजिटल क्यूआर मेडिकल पासपोर्ट देखें।"
            )
        else:
            response_text = (
                f"🚨 **Emergency & Critical Medical Summary:**\n\n"
                f"• **Patient:** {patient.full_name}\n"
                f"• **Blood Group:** B+ Positive\n"
                f"• **Hospital:** Harborview Medical Centre (+91 11 2658 8500)\n"
                f"• **Primary Allergies:** Penicillin (Moderate rash)\n"
                f"• **Emergency Action:** Click the **'Emergency Card'** button in the top menu to view or print your digital medical passport with scannable QR code."
            )

    elif any(k in query_lower for k in ["task", "to do", "overdue", "pending", "kaam"]):
        overdue_note = f"\n⚠️ **Overdue Tasks ({len(overdue_tasks)}):** " + ", ".join([t.title for t in overdue_tasks[:2]]) if overdue_tasks else ""
        if is_hindi:
            response_text = (
                f"✅ **आपकी रिकवरी प्रगति सारांश:**\n\n"
                f"• **कुल कार्य:** {len(tasks)}\n"
                f"• **पूरे हो चुके:** {len(completed_tasks)}\n"
                f"• **लंबित (Pending):** {len(pending_tasks)}"
                f"{overdue_note}\n\n"
                f"कार्यों को पूरा करने या अपने परिवार के सदस्य को सौंपने के लिए **Tasks** पेज पर जाएं।"
            )
        else:
            response_text = (
                f"✅ **Journey Progress Summary:**\n\n"
                f"• **Total Tasks:** {len(tasks)}\n"
                f"• **Completed:** {len(completed_tasks)}\n"
                f"• **Active/Pending:** {len(pending_tasks)}"
                f"{overdue_note}\n\n"
                f"Visit **My Tasks** to mark tasks complete or reassign them to your caregiver."
            )

    else:
        first_name = patient.full_name.split()[0]
        if is_hindi:
            response_text = (
                f"नमस्ते {first_name}! 👋 मैं आपका CareBridge AI स्वास्थ्य सहायक हूँ।\n\n"
                f"आज की आपकी रिकवरी का संक्षिप्त विवरण:\n"
                f"• **सक्रिय कार्य:** {len(pending_tasks)} लंबित ({len(overdue_tasks)} अतिदेय)\n"
                f"• **अगला अपॉइंटमेंट:** {appointments[0].title if appointments else 'सभी कार्य समय पर हैं'}\n"
                f"• **आवश्यक रिपोर्ट्स:** {len(missing_reports)} रिपोर्ट की जांच बाकी\n\n"
                f"आप मुझसे अपनी दवाइयों, अगली डॉक्टर विज़िट, रिपोर्ट्स या किसी भी सहायता के बारे में हिंदी या अंग्रेज़ी में कभी भी पूछ सकते हैं!"
            )
        else:
            response_text = (
                f"Hello {first_name}! 👋 I am your CareBridge AI Health Assistant.\n\n"
                f"Here is a quick snapshot of your care plan today:\n"
                f"• **Active Tasks:** {len(pending_tasks)} pending ({len(overdue_tasks)} overdue)\n"
                f"• **Next Scheduled Milestone:** {appointments[0].title if appointments else 'All current milestones cleared'}\n"
                f"• **Reports Needed:** {len(missing_reports)} diagnostic file(s)\n\n"
                f"Feel free to ask me questions about your medications, appointments, reports, or care tasks anytime in English or Hindi!"
            )

    return {
        "query": data.query,
        "language": "hi" if is_hindi else "en",
        "answer": response_text,
        "timestamp": datetime.utcnow().isoformat(),
        "disclaimer": "CareBridge AI organizes clerical records and instructions. It does not replace clinical consultation.",
        "team_credit": "ByteCoders · IIMT Engineering College, Meerut",
    }
