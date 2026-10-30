from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import AccessBarrier, JourneyTask, User
from app.schemas.common import BarrierCreate, BarrierUpdate
from app.services.permissions import patient_id_for_user, require_patient

router = APIRouter(prefix="/api/barriers", tags=["access barriers"])


@router.get("")
def list_barriers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    return db.query(AccessBarrier).filter_by(patient_id=patient_id).order_by(AccessBarrier.barrier_date.desc()).all()


@router.post("", status_code=201)
def create_barrier(data: BarrierCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    if data.related_task_id and not db.query(JourneyTask).filter_by(id=data.related_task_id, patient_id=user.id).first():
        raise HTTPException(status_code=400, detail="Related task does not belong to this patient.")
    barrier = AccessBarrier(patient_id=user.id, **data.model_dump())
    db.add(barrier)
    db.commit()
    db.refresh(barrier)
    return barrier


@router.put("/{barrier_id}")
def update_barrier(barrier_id: int, data: BarrierUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    barrier = db.query(AccessBarrier).filter_by(id=barrier_id, patient_id=user.id).first()
    if not barrier:
        raise HTTPException(status_code=404, detail="Access barrier not found.")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(barrier, key, value)
    db.commit()
    return barrier
