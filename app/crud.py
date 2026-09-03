"""Бизнес-логика поверх ORM-моделей.

Содержит два содержательных правила предметной области:
1. У комиссии не может быть более одного действующего председателя.
2. Заседание нельзя пометить как "проведено" без кворума —
   присутствовать должно больше половины членов комиссии.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas


class DomainError(Exception):
    """Базовая ошибка бизнес-правила (маппится в HTTP 409/422 в роутере)."""


class NotFoundError(Exception):
    pass


class ConflictError(DomainError):
    pass


class QuorumError(DomainError):
    pass


# ---------- Deputies ----------
def create_deputy(db: Session, data: schemas.DeputyCreate) -> models.Deputy:
    deputy = models.Deputy(**data.model_dump())
    db.add(deputy)
    db.commit()
    db.refresh(deputy)
    return deputy


def list_deputies(db: Session, active_only: bool = False) -> list[models.Deputy]:
    stmt = select(models.Deputy)
    if active_only:
        stmt = stmt.where(models.Deputy.is_active.is_(True))
    return list(db.scalars(stmt))


def get_deputy(db: Session, deputy_id: int) -> models.Deputy:
    deputy = db.get(models.Deputy, deputy_id)
    if deputy is None:
        raise NotFoundError(f"Депутат id={deputy_id} не найден")
    return deputy


def update_deputy(db: Session, deputy_id: int, data: schemas.DeputyUpdate) -> models.Deputy:
    deputy = get_deputy(db, deputy_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(deputy, field, value)
    db.commit()
    db.refresh(deputy)
    return deputy


def delete_deputy(db: Session, deputy_id: int) -> None:
    deputy = get_deputy(db, deputy_id)
    db.delete(deputy)
    db.commit()


# ---------- Commissions ----------
def create_commission(db: Session, data: schemas.CommissionCreate) -> models.Commission:
    commission = models.Commission(**data.model_dump())
    db.add(commission)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Комиссия с таким названием уже существует") from exc
    db.refresh(commission)
    return commission


def list_commissions(db: Session) -> list[models.Commission]:
    return list(db.scalars(select(models.Commission)))


def get_commission(db: Session, commission_id: int) -> models.Commission:
    commission = db.get(models.Commission, commission_id)
    if commission is None:
        raise NotFoundError(f"Комиссия id={commission_id} не найдена")
    return commission


def add_membership(
    db: Session, commission_id: int, data: schemas.MembershipCreate
) -> models.CommissionMembership:
    commission = get_commission(db, commission_id)
    get_deputy(db, data.deputy_id)

    # Правило: у комиссии может быть только один действующий председатель.
    if data.is_chair:
        existing_chair = db.scalar(
            select(models.CommissionMembership).where(
                models.CommissionMembership.commission_id == commission.id,
                models.CommissionMembership.is_chair.is_(True),
            )
        )
        if existing_chair is not None:
            raise ConflictError(
                "У комиссии уже есть действующий председатель "
                f"(deputy_id={existing_chair.deputy_id}). "
                "Сначала снимите полномочия текущего председателя."
            )

    membership = models.CommissionMembership(commission_id=commission.id, **data.model_dump())
    db.add(membership)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Этот депутат уже состоит в данной комиссии") from exc
    db.refresh(membership)
    return membership


def list_memberships(db: Session, commission_id: int) -> list[models.CommissionMembership]:
    get_commission(db, commission_id)
    stmt = select(models.CommissionMembership).where(
        models.CommissionMembership.commission_id == commission_id
    )
    return list(db.scalars(stmt))


# ---------- Meetings ----------
def create_meeting(db: Session, data: schemas.MeetingCreate) -> models.Meeting:
    if data.commission_id is not None:
        get_commission(db, data.commission_id)
    meeting = models.Meeting(**data.model_dump())
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def list_meetings(db: Session, commission_id: int | None = None) -> list[models.Meeting]:
    stmt = select(models.Meeting)
    if commission_id is not None:
        stmt = stmt.where(models.Meeting.commission_id == commission_id)
    return list(db.scalars(stmt))


def get_meeting(db: Session, meeting_id: int) -> models.Meeting:
    meeting = db.get(models.Meeting, meeting_id)
    if meeting is None:
        raise NotFoundError(f"Заседание id={meeting_id} не найдено")
    return meeting


def set_meeting_status(
    db: Session, meeting_id: int, new_status: models.MeetingStatus
) -> models.Meeting:
    meeting = get_meeting(db, meeting_id)

    if new_status == models.MeetingStatus.held:
        _ensure_quorum(db, meeting)

    meeting.status = new_status
    db.commit()
    db.refresh(meeting)
    return meeting


def _ensure_quorum(db: Session, meeting: models.Meeting) -> None:
    """Правило кворума: заседание комиссии проводится, только если
    присутствует более половины членов этой комиссии.
    Для пленарных заседаний (commission_id is None) правило не применяется.
    """
    if meeting.commission_id is None:
        return

    total_members = len(
        list(
            db.scalars(
                select(models.CommissionMembership).where(
                    models.CommissionMembership.commission_id == meeting.commission_id
                )
            )
        )
    )
    if total_members == 0:
        raise QuorumError("В комиссии нет ни одного члена — заседание провести нельзя")

    present_count = len(
        list(
            db.scalars(
                select(models.Attendance).where(
                    models.Attendance.meeting_id == meeting.id,
                    models.Attendance.status == models.AttendanceStatus.present,
                )
            )
        )
    )
    required = total_members // 2 + 1
    if present_count < required:
        raise QuorumError(
            f"Нет кворума: присутствует {present_count} из {total_members} членов комиссии, "
            f"требуется не менее {required}"
        )


# ---------- Attendance ----------
def mark_attendance(
    db: Session, meeting_id: int, data: schemas.AttendanceCreate
) -> models.Attendance:
    get_meeting(db, meeting_id)
    get_deputy(db, data.deputy_id)

    attendance = models.Attendance(meeting_id=meeting_id, **data.model_dump())
    db.add(attendance)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "Посещаемость для этого депутата на этом заседании уже отмечена"
        ) from exc
    db.refresh(attendance)
    return attendance


def list_attendance(db: Session, meeting_id: int) -> list[models.Attendance]:
    get_meeting(db, meeting_id)
    stmt = select(models.Attendance).where(models.Attendance.meeting_id == meeting_id)
    return list(db.scalars(stmt))


def deputy_attendance_stats(db: Session, deputy_id: int) -> dict:
    """Отчёт по посещаемости конкретного депутата (для отчётов по периодам)."""
    get_deputy(db, deputy_id)
    records = list(
        db.scalars(select(models.Attendance).where(models.Attendance.deputy_id == deputy_id))
    )
    total = len(records)
    present = sum(1 for r in records if r.status == models.AttendanceStatus.present)
    return {
        "deputy_id": deputy_id,
        "total_meetings": total,
        "present": present,
        "absent": sum(1 for r in records if r.status == models.AttendanceStatus.absent),
        "excused": sum(1 for r in records if r.status == models.AttendanceStatus.excused),
        "attendance_rate": round(present / total, 2) if total else None,
    }
