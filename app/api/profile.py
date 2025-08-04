from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import UserRepository
from app.core.security import verify_password, hash_password, require_token_type
from app.schemas.auth import (
    ProfileResponse,
    ProfileUpdateRequest,
    ChangePasswordRequest,
)
from app.domain.entities import User
from app.api.auth import bearer_scheme
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    dependencies=[Depends(bearer_scheme)],  # Lock endpoints in Swagger UI
)


# Helper to extract and validate access token from credentials
def get_access_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return require_token_type(credentials.credentials, "access")


@router.get("/me", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # Assume you have a way to get role name from role_id, else leave as str(role_id)
    role_name = str(user.role_id)
    return ProfileResponse(
        id=str(user.id), full_name=user.full_name, email=user.email, role=role_name
    )


@router.put("/me", response_model=ProfileResponse)
def update_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    update_data = {}
    if data.full_name is not None:
        update_data["full_name"] = data.full_name
    if data.email is not None:
        update_data["email"] = data.email
    updated = user_repo.update(current_user.id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found.")
    role_name = str(updated.role_id)
    return ProfileResponse(
        id=str(updated.id),
        full_name=updated.full_name,
        email=updated.email,
        role=role_name,
    )


@router.put("/me/change-password", response_model=dict)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect.")
    user.password = hash_password(data.new_password)
    user_repo.update(user.id, password=user.password)
    return {"message": "Password changed successfully."}
