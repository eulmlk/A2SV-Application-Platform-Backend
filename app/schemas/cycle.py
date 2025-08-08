from pydantic import BaseModel
from datetime import date, datetime
from typing import List


class PublicCycleResponse(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime
    description: str | None = None


class PublicCycleListResponse(BaseModel):
    cycles: List[PublicCycleResponse]
    total_count: int
    page: int
    limit: int
