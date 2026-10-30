import json
from typing import Optional

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings


class SuggestedTask(BaseModel):
    title: str = Field(min_length=2, max_length=220)
    description: str = ""
    category: str = "Other"
    due_date: str | None = None
    source_text: str
    needs_verification: bool = True


class DocumentAnalysis(BaseModel):
    document_type: str = "Unknown"
    document_date: str | None = None
    hospital_name: str | None = None
    appointments: list[str] = Field(default_factory=list)
    follow_up_instructions: list[str] = Field(default_factory=list)
    required_reports: list[str] = Field(default_factory=list)
    clinician_tasks: list[SuggestedTask] = Field(default_factory=list)
    medication_information: list[str] = Field(default_factory=list)
    administrative_instructions: list[str] = Field(default_factory=list)
    uncertain_fields: list[str] = Field(default_factory=list)
    simple_explanation: str


SYSTEM_PROMPT = """You extract information from patient-provided clinician documents. This is a clerical organization tool, not a medical advisor. Do not diagnose, recommend, infer missing instructions, or alter medication names, doses, or schedules. Keep medication text verbatim. Only create tasks from explicit clinician instructions, preserve the exact supporting source_text, set needs_verification true, and use null for unknown dates or names. List unclear fields in uncertain_fields. Do not treat administrative tasks as medical advice. Return only JSON matching the requested structure. Explain in simple language while clearly saying the patient must verify the summary with their clinician."""


def analyze_document(text: str, image_data_url: Optional[str] = None) -> tuple[dict, str]:
    if settings.ai_api_key:
        endpoint = settings.ai_base_url.rstrip("/") + "/chat/completions"
        user_content = [{"type": "text", "text": "Extract the requested fields from this document text. Keep source_text exact.\n\n" + text[:30000]}]
        if image_data_url:
            user_content.append({"type": "image_url", "image_url": {"url": image_data_url, "detail": "high"}})
        response = httpx.post(
            endpoint,
            headers={"Authorization": f"Bearer {settings.ai_api_key}"},
            json={
                "model": settings.ai_model,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0,
            },
            timeout=60,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        try:
            parsed = DocumentAnalysis.model_validate_json(raw)
        except ValidationError as exc:
            raise ValueError("AI output did not match the required document structure. Please try again.") from exc
        return parsed.model_dump(), "ai"

    # Demo mode intentionally makes no clinical interpretation from arbitrary uploads.
    # It returns the source text for human review and clearly labels the analysis as simulated.
    simulated = DocumentAnalysis(
        document_type="Uploaded document (simulated review)",
        uncertain_fields=["Document type", "Dates", "Instructions", "Required reports"],
        simple_explanation="This is a simulated demo review. No AI medical analysis was performed. Review the extracted text yourself and confirm any task with your care team before adding it to your journey.",
    )
    return simulated.model_dump(), "simulated"
