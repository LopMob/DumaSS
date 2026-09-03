from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/deputies", tags=["Депутаты"])


@router.post("", response_model=schemas.DeputyOut, status_code=201)
def create_deputy(data: schemas.DeputyCreate, db: Session = Depends(get_db)):
    return crud.create_deputy(db, data)


@router.get("", response_model=list[schemas.DeputyOut])
def list_deputies(active_only: bool = Query(False), db: Session = Depends(get_db)):
    return crud.list_deputies(db, active_only)


@router.get("/{deputy_id}", response_model=schemas.DeputyOut)
def get_deputy(deputy_id: int, db: Session = Depends(get_db)):
    return crud.get_deputy(db, deputy_id)


@router.patch("/{deputy_id}", response_model=schemas.DeputyOut)
def update_deputy(deputy_id: int, data: schemas.DeputyUpdate, db: Session = Depends(get_db)):
    return crud.update_deputy(db, deputy_id, data)


@router.delete("/{deputy_id}", status_code=204)
def delete_deputy(deputy_id: int, db: Session = Depends(get_db)):
    crud.delete_deputy(db, deputy_id)


@router.get("/{deputy_id}/attendance-stats")
def deputy_attendance_stats(deputy_id: int, db: Session = Depends(get_db)):
    return crud.deputy_attendance_stats(db, deputy_id)
