from pydantic import BaseModel
from datetime import date, datetime

class PublicCycleResponse(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime 