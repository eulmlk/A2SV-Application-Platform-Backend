from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import ApplicationCycleRepository
from app.schemas.cycle import PublicCycleResponse
from app.schemas.base import APIResponse

router = APIRouter(prefix="/cycles", tags=["cycles"])

@router.get("/", response_model=APIResponse[list[PublicCycleResponse]])
def get_all_cycles(db: Session = Depends(get_db)):
    repo = ApplicationCycleRepository(db)
    cycles = repo.list_all()
    response_data = [PublicCycleResponse(
        id=c.id,
        name=c.name,
        start_date=c.start_date,
        end_date=c.end_date,
        is_active=c.is_active,
        created_at=c.created_at
    ) for c in cycles]
    return APIResponse(data=response_data, message="Cycles retrieved successfully.")

@router.get("/{cycle_id}/", response_model=APIResponse[PublicCycleResponse])
def get_cycle_by_id(cycle_id: int, db: Session = Depends(get_db)):
    repo = ApplicationCycleRepository(db)
    c = repo.get_by_id(cycle_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cycle not found.")
    response_data = PublicCycleResponse(
        id=c.id,
        name=c.name,
        start_date=c.start_date,
        end_date=c.end_date,
        is_active=c.is_active,
        created_at=c.created_at
        ) 
    return APIResponse(data=response_data, message="Cycle retrieved successfully.")