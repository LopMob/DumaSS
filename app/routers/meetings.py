from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import MeetingStatus

router = APIRouter(prefix="/meetings", tags=["Заседания"])


@router.post("", response_model=schemas.MeetingOut, status_code=201)
def create_meeting(data: schemas.MeetingCreate, db: Session = Depends(get_db)):
    return crud.create_meeting(db, data)


@router.get("", response_model=list[schemas.MeetingOut])
def list_meetings(
    commission_id: int | None = Query(None),
    status: MeetingStatus | None = Query(None),
    db: Session = Depends(get_db),
):
    """Список заседаний. Поддерживает фильтрацию по комиссии и по статусу."""
    return crud.list_meetings(db, commission_id, status)


@router.get("/{meeting_id}", response_model=schemas.MeetingOut)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    return crud.get_meeting(db, meeting_id)


@router.patch("/{meeting_id}/status", response_model=schemas.MeetingOut)
def set_meeting_status(
    meeting_id: int, data: schemas.MeetingStatusUpdate, db: Session = Depends(get_db)
):
    """Смена статуса заседания. Перевод в 'held' проверяет правило кворума."""
    return crud.set_meeting_status(db, meeting_id, data.status)


@router.post("/{meeting_id}/attendance", response_model=schemas.AttendanceOut, status_code=201)
def mark_attendance(meeting_id: int, data: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    return crud.mark_attendance(db, meeting_id, data)


@router.get("/{meeting_id}/attendance", response_model=list[schemas.AttendanceOut])
def list_attendance(meeting_id: int, db: Session = Depends(get_db)):
    return crud.list_attendance(db, meeting_id)
