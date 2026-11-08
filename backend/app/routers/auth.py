import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database.connection import get_db
from app.database.models import CaregiverRelationship, HealthcareJourney, PatientProfile, User
from app.schemas.common import LoginInput, RegisterInput, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    if data.role == "caregiver" and not data.invite_code:
        raise HTTPException(status_code=400, detail="Caregiver registration requires an invitation code from a patient.")
    user = User(email=email, full_name=data.full_name, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    db.flush()
    if data.role == "patient":
        db.add(PatientProfile(user_id=user.id))
        db.add(HealthcareJourney(patient_id=user.id))
    else:
        invitation = db.query(CaregiverRelationship).filter_by(invitation_code=data.invite_code, invited_email=email, caregiver_user_id=None).first()
        if not invitation:
            db.rollback()
            raise HTTPException(status_code=400, detail="This invitation is invalid, already used, or belongs to another email.")
        invitation.caregiver_user_id = user.id
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(user.id), user=user)


@router.post("/login", response_model=TokenOut)
@router.post("/token", response_model=TokenOut)
def login(data: LoginInput, db: Session = Depends(get_db)):
    email = (data.email or data.username or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")
    user = db.query(User).filter_by(email=email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return TokenOut(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
