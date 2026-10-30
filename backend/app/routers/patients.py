from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import PatientProfile, User
from app.schemas.common import ProfileUpdate
from app.services.permissions import patient_id_for_user, require_patient

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("/me")
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    patient = db.get(User, patient_id)
    profile = db.query(PatientProfile).filter_by(user_id=patient_id).first()
    if user.role == "caregiver":
        return {"id": patient.id, "full_name": patient.full_name, "is_demo": patient.is_demo}
    return {"id": patient.id, "full_name": patient.full_name, "email": patient.email, "role": patient.role,
            "phone": profile.phone if profile else None, "date_of_birth": profile.date_of_birth if profile else None,
            "preferred_language": profile.preferred_language if profile else "English", "hospital_name": profile.hospital_name if profile else None,
            "is_demo": patient.is_demo}


@router.put("/me")
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    profile = db.query(PatientProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    return {"ok": True}
