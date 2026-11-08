from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["patient", "caregiver"] = "patient"
    invite_code: str | None = None


class LoginInput(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str


class UserOut(ORMModel):
    id: int
    email: str
    full_name: str
    role: str
    is_demo: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=220)
    description: str = ""
    category: str = "Other"
    status: str = "Pending"
    due_date: date | None = None
    assigned_to_id: int | None = None
    needs_clinician_verification: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=220)
    description: str | None = None
    category: str | None = None
    status: str | None = None
    due_date: date | None = None
    assigned_to_id: int | None = None
    needs_clinician_verification: bool | None = None


class TaskStatusInput(BaseModel):
    status: str


class TaskOut(ORMModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    due_date: date | None
    completed_at: datetime | None
    source_document_id: int | None
    source_instruction: str | None
    needs_clinician_verification: bool
    assigned_to_id: int | None


class ReportCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    appointment_date: date | None = None
    status: Literal["Available", "Missing", "Pending Upload", "Needs Verification"] = "Missing"
    notes: str = ""


class ReportUpdate(BaseModel):
    status: Literal["Available", "Missing", "Pending Upload", "Needs Verification", "Verified"] | None = None
    document_id: int | None = None
    notes: str | None = None


class ReportOut(ORMModel):
    id: int
    name: str
    appointment_date: date | None
    status: str
    document_id: int | None
    notes: str


class CaregiverInvite(BaseModel):
    email: EmailStr


class TaskAssignment(BaseModel):
    task_id: int
    caregiver_id: int


class BarrierCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    description: str = ""
    category: str = "Other"
    related_task_id: int | None = None
    status: str = "Open"
    follow_up_notes: str = ""


class BarrierUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    status: str | None = None
    follow_up_notes: str | None = None


class BarrierOut(ORMModel):
    id: int
    title: str
    description: str
    category: str
    barrier_date: datetime
    related_task_id: int | None
    status: str
    follow_up_notes: str


class NotificationOut(ORMModel):
    id: int
    title: str
    message: str
    kind: str
    is_read: bool
    created_at: datetime


class ProfileUpdate(BaseModel):
    phone: str | None = None
    preferred_language: str | None = None
    hospital_name: str | None = None
