import json
import base64
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.time import utc_now
from app.database.connection import get_db
from app.database.models import Document, ExtractedDocumentData, JourneyTask, User
from app.services.ai_service import analyze_document
from app.services.audit import log_action
from app.services.ocr_service import OCRUnavailable, extract_text
from app.services.permissions import require_patient

router = APIRouter(prefix="/api/documents", tags=["documents"])
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


class ApprovedTask(BaseModel):
    title: str = Field(min_length=2, max_length=220)
    description: str = ""
    category: str = "Other"
    due_date: str | None = None
    source_text: str = ""


class ConfirmDocument(BaseModel):
    confirmed: bool
    tasks: list[ApprovedTask] = Field(default_factory=list)


class AnalyzeConsent(BaseModel):
    consent: bool


@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Upload a PDF, JPG, JPEG, or PNG file.")
    payload = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not payload:
        raise HTTPException(status_code=400, detail="The selected file is empty.")
    if len(payload) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Files must be {settings.max_upload_mb} MB or smaller.")
    signatures = {".pdf": payload.startswith(b"%PDF-"), ".png": payload.startswith(b"\x89PNG\r\n\x1a\n"),
                  ".jpg": payload.startswith(b"\xff\xd8\xff"), ".jpeg": payload.startswith(b"\xff\xd8\xff")}
    if not signatures.get(suffix, False):
        raise HTTPException(status_code=415, detail="The file contents do not match its extension. Choose a valid PDF, JPG, JPEG, or PNG.")
    upload_root = Path(settings.upload_dir).resolve()
    upload_root.mkdir(parents=True, exist_ok=True)
    stored_name = f"{user.id}_{__import__('secrets').token_hex(12)}{suffix}"
    destination = upload_root / stored_name
    destination.write_bytes(payload)
    document = Document(patient_id=user.id, filename=Path(file.filename).name, content_type=file.content_type, storage_path=str(destination))
    db.add(document)
    db.flush()
    log_action(db, user.id, "document.uploaded", "document", document.id)
    db.commit()
    return {"id": document.id, "filename": document.filename, "content_type": document.content_type, "size": len(payload), "created_at": document.created_at}


def _owned_document(db: Session, user: User, document_id: int) -> Document:
    document = db.query(Document).filter_by(id=document_id, patient_id=user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.get("")
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can access their document library.")
    docs = db.query(Document).filter_by(patient_id=user.id).order_by(Document.created_at.desc()).all()
    return [{"id": d.id, "filename": d.filename, "content_type": d.content_type, "document_type": d.document_type,
             "document_date": d.document_date, "analyzed": d.analyzed, "confirmed": d.confirmed, "analysis_mode": d.analysis_mode,
             "created_at": d.created_at} for d in docs]


@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = _owned_document(db, user, document_id)
    analysis = json.loads(document.analysis_json) if document.analysis_json else None
    return {"id": document.id, "filename": document.filename, "content_type": document.content_type,
            "document_type": document.document_type, "document_date": document.document_date, "hospital_name": document.hospital_name,
            "extracted_text": document.extracted_text, "explanation": document.explanation, "analysis": analysis,
            "analysis_mode": document.analysis_mode, "analyzed": document.analyzed, "confirmed": document.confirmed,
            "created_at": document.created_at}


@router.get("/{document_id}/preview")
def preview_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = _owned_document(db, user, document_id)
    if document.storage_path.startswith("demo://"):
        return StreamingResponse(BytesIO(document.extracted_text.encode("utf-8")), media_type="text/plain",
                                 headers={"Content-Disposition": "inline; filename=fictional-demo-document.txt"})
    path = Path(document.storage_path).resolve()
    upload_root = Path(settings.upload_dir).resolve()
    if upload_root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Document file is no longer available.")
    return FileResponse(path, media_type=document.content_type, filename=document.filename, content_disposition_type="inline")


@router.post("/{document_id}/analyze")
def analyze(document_id: int, consent: AnalyzeConsent, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = _owned_document(db, user, document_id)
    if not consent.consent:
        raise HTTPException(status_code=400, detail="Consent is required before document analysis.")
    if not document.consent_at:
        document.consent_at = utc_now()
        log_action(db, user.id, "document.processing_consent", "document", document.id)
        db.commit()
    try:
        if not document.extracted_text and not document.storage_path.startswith("demo://"):
            document.extracted_text = extract_text(document.storage_path, document.content_type)
        if not document.extracted_text.strip():
            raise OCRUnavailable("No readable text was found. Please upload a clearer copy.")
    except OCRUnavailable as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        image_data_url = None
        if settings.ai_api_key and document.content_type in {"image/jpeg", "image/png"} and not document.storage_path.startswith("demo://"):
            image_bytes = Path(document.storage_path).read_bytes()
            encoded = base64.b64encode(image_bytes).decode("ascii")
            image_data_url = f"data:{document.content_type};base64,{encoded}"
        data, mode = analyze_document(document.extracted_text, image_data_url=image_data_url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Document analysis could not be completed. Please review the extracted text or try again.") from exc
    document.analysis_json = json.dumps(data)
    document.document_type = data.get("document_type")
    document.document_date = data.get("document_date")
    document.hospital_name = data.get("hospital_name")
    document.explanation = data.get("simple_explanation")
    document.analysis_mode = mode
    document.analyzed = True
    extracted = db.query(ExtractedDocumentData).filter_by(document_id=document.id).first()
    if extracted:
        extracted.structured_json = json.dumps(data)
    else:
        db.add(ExtractedDocumentData(document_id=document.id, structured_json=json.dumps(data)))
    db.commit()
    return {"id": document.id, "extracted_text": document.extracted_text, "analysis": data, "analysis_mode": mode,
            "notice": "Simulated demo review. No AI analysis was performed." if mode == "simulated" else "AI output is a draft. Verify every field before confirming."}


@router.post("/{document_id}/confirm")
def confirm(document_id: int, data: ConfirmDocument, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = _owned_document(db, user, document_id)
    if not data.confirmed:
        raise HTTPException(status_code=400, detail="Explicit confirmation is required before creating tasks.")
    if not document.analyzed:
        raise HTTPException(status_code=409, detail="Analyze the document before confirming tasks.")
    created = []
    for approved in data.tasks:
        if not approved.source_text or approved.source_text not in document.extracted_text:
            raise HTTPException(status_code=422, detail="Each confirmed task must cite exact supporting text from the extracted document.")
        task = JourneyTask(patient_id=user.id, title=approved.title, description=approved.description,
                           category=approved.category, status="Needs Verification", source_document_id=document.id,
                           source_instruction=approved.source_text or None, needs_clinician_verification=True)
        if approved.due_date:
            from datetime import date
            try:
                task.due_date = date.fromisoformat(approved.due_date)
            except ValueError:
                task.due_date = None
        db.add(task)
        db.flush()
        created.append(task.id)
    document.confirmed = True
    document_data = db.query(ExtractedDocumentData).filter_by(document_id=document.id).first()
    if document_data:
        document_data.confirmed_at = utc_now()
    log_action(db, user.id, "document.confirmed", "document", document.id)
    db.commit()
    return {"confirmed": True, "created_task_ids": created}


@router.delete("/{document_id}", status_code=200)
def delete_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = _owned_document(db, user, document_id)
    db.query(JourneyTask).filter_by(source_document_id=document.id).update({"source_document_id": None})
    db.query(ExtractedDocumentData).filter_by(document_id=document.id).delete()
    from app.database.models import RequiredReport
    db.query(RequiredReport).filter_by(supporting_document_id=document.id).update({"supporting_document_id": None, "status": "Missing"})
    if not document.storage_path.startswith("demo://"):
        try:
            p = Path(document.storage_path)
            if p.is_file():
                p.unlink()
        except OSError:
            pass
    db.delete(document)
    log_action(db, user.id, "document.deleted", "document", document.id)
    db.commit()
    return {"message": "Document deleted successfully", "id": document_id}
