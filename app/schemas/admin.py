from pydantic import BaseModel, EmailStr
from typing import List
from datetime import date, datetime


class AdminCreateUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str


class AdminUserResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: str
    profile_picture: str | None = None


class AdminCycleCreateRequest(BaseModel):
    name: str
    start_date: date
    end_date: date
    description: str | None = None


class AdminCycleResponse(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime
    description: str | None = None


class AdminUpdateUserRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None


class AdminUpdateCycleRequest(BaseModel):
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class AdminListUsersResponse(BaseModel):
    users: List[AdminUserResponse]
    total_count: int
    page: int
    limit: int
