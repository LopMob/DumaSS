from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import AttendanceStatus, MeetingStatus


# ---------- Deputy ----------
class DeputyCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    party: str | None = None
    election_district: str | None = None


class DeputyUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    party: str | None = None
    election_district: str | None = None
    is_active: bool | None = None


class DeputyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    party: str | None
    election_district: str | None
    is_active: bool


# ---------- Commission ----------
class CommissionCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None


class CommissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None


class MembershipCreate(BaseModel):
    deputy_id: int
    is_chair: bool = False


class MembershipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    commission_id: int
    deputy_id: int
    is_chair: bool
    joined_at: date


# ---------- Meeting ----------
class MeetingCreate(BaseModel):
    commission_id: int | None = None
    title: str = Field(min_length=2, max_length=255)
    scheduled_at: datetime
    agenda: str | None = None


class MeetingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    commission_id: int | None
    title: str
    scheduled_at: datetime
    status: MeetingStatus
    agenda: str | None


class MeetingStatusUpdate(BaseModel):
    status: MeetingStatus


# ---------- Attendance ----------
class AttendanceCreate(BaseModel):
    deputy_id: int
    status: AttendanceStatus
    note: str | None = None


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    meeting_id: int
    deputy_id: int
    status: AttendanceStatus
    note: str | None


class ErrorResponse(BaseModel):
    detail: str
