from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/commissions", tags=["Комиссии"])


@router.post("", response_model=schemas.CommissionOut, status_code=201)
def create_commission(data: schemas.CommissionCreate, db: Session = Depends(get_db)):
    return crud.create_commission(db, data)


@router.get("", response_model=list[schemas.CommissionOut])
def list_commissions(db: Session = Depends(get_db)):
    return crud.list_commissions(db)


@router.get("/{commission_id}", response_model=schemas.CommissionOut)
def get_commission(commission_id: int, db: Session = Depends(get_db)):
    return crud.get_commission(db, commission_id)


@router.post("/{commission_id}/members", response_model=schemas.MembershipOut, status_code=201)
def add_member(commission_id: int, data: schemas.MembershipCreate, db: Session = Depends(get_db)):
    """Добавить депутата в комиссию. is_chair=true назначает председателя
    (правило: председатель у комиссии может быть только один)."""
    return crud.add_membership(db, commission_id, data)


@router.get("/{commission_id}/members", response_model=list[schemas.MembershipOut])
def list_members(commission_id: int, db: Session = Depends(get_db)):
    return crud.list_memberships(db, commission_id)
