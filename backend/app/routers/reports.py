from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import Document, RequiredReport, User
from app.schemas.common import ReportCreate, ReportUpdate
from app.services.permissions import patient_id_for_user, require_patient

router = APIRouter(prefix="/api/reports", tags=["report readiness"])
READY_STATES = {"Verified"}


@router.get("/readiness")
def readiness(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    reports = db.query(RequiredReport).filter_by(patient_id=patient_id).order_by(RequiredReport.appointment_date.asc().nullslast()).all()
    available = sum(1 for r in reports if r.status in READY_STATES)
    return {"readiness_percentage": round(available / len(reports) * 100) if reports else 0,
            "available_count": available, "total_count": len(reports), "documents_only": True,
            "notice": "This checklist tracks document availability only. It does not assess medical readiness.",
            "reports": [{"id": r.id, "name": r.name, "status": r.status, "appointment_date": r.appointment_date,
                         "document_id": r.document_id, "notes": r.notes} for r in reports]}


@router.post("", status_code=201)
def create_report(data: ReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    report = RequiredReport(patient_id=user.id, **data.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.patch("/{report_id}")
def update_report(report_id: int, data: ReportUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    report = db.query(RequiredReport).filter_by(id=report_id, patient_id=user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Required report not found.")
    values = data.model_dump(exclude_unset=True)
    status_value = values.get("status")
    document_id = values.get("document_id")
    if document_id is not None and not db.query(Document).filter_by(id=document_id, patient_id=user.id).first():
        raise HTTPException(status_code=400, detail="The document does not belong to this patient.")
    if status_value == "Verified" and not (document_id or report.document_id):
        raise HTTPException(status_code=400, detail="Attach a document before marking this report verified.")
    if status_value:
        report.status = status_value
    if document_id is not None:
        report.document_id = document_id
    if "notes" in values and values["notes"] is not None:
        report.notes = values["notes"]
    db.commit()
    return {"ok": True}
