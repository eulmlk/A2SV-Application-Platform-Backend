from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import ApplicationCycleRepository
from app.schemas.cycle import PublicCycleResponse, PublicCycleListResponse
from app.schemas.base import APIResponse
from app.api.auth import bearer_scheme
from app.core.security import require_token_type
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(prefix="/cycles", tags=["cycles"])


# Helper to extract and validate access token from credentials
def get_access_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return require_token_type(credentials.credentials, "access")


@router.get("/", response_model=APIResponse[PublicCycleListResponse])
def get_all_cycles(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    repo = ApplicationCycleRepository(db)
    offset = (page - 1) * limit
    cycles = repo.list_all(offset=offset, limit=limit)
    total_count = (
        repo.count_all() if hasattr(repo, "count_all") else len(repo.list_all())
    )
    response_data = PublicCycleListResponse(
        cycles=[
            PublicCycleResponse(
                id=c.id,
                name=c.name,
                start_date=c.start_date,
                end_date=c.end_date,
                is_active=c.is_active,
                created_at=c.created_at,
                description=c.description if c.description else None,
            )
            for c in cycles
        ],
        total_count=total_count,
        page=page,
        limit=limit,
    )
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
        created_at=c.created_at,
        description=c.description if c.description else None,
    )
    return APIResponse(data=response_data, message="Cycle retrieved successfully.")
