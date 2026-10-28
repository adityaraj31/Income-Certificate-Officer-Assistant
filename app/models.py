from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class Officer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    designation: str
    username: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    applicant_name_hi: str
    father_name_hi: str
    aadhaar_last4: str
    address_text_hi: str
    occupation_hi: str
    stated_income_monthly: int
    family_members: int
    village: str
    tehsil: str
    district: str
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sla_due_at: datetime
    status: str = Field(default="पेंडिंग")
    flags_json: str = Field(default="[]")
    aadhaar_name_hi: Optional[str] = None


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    doc_type: str
    issued_on: Optional[datetime] = None
    expires_on: Optional[datetime] = None
    number_masked: Optional[str] = None
    file_ref: Optional[str] = None


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    officer_id: int = Field(foreign_key="officer.id")
    ai_suggestion_json: str
    officer_decision: str
    agreed: bool
    remark: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
