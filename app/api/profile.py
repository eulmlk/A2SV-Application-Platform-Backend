from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import os
import uuid
import cloudinary.uploader
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import UserRepository, RoleRepository
from app.core.security import verify_password, hash_password, require_token_type
from app.schemas.auth import (
    ProfileResponse,
    ChangePasswordRequest,
)
from app.domain.entities import User
from app.api.auth import bearer_scheme
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.base import APIResponse

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


@router.get("/me", response_model=APIResponse[ProfileResponse])
def get_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user = user_repo.get_by_id(current_user.id)
    role = role_repo.get_by_id(user.role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    response_data = ProfileResponse(
        id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        role=role.name,
        profile_picture_url=user.profile_picture_url,
    )

    return APIResponse(data=response_data, message="Profile fetched successfully.")


# Accept both JSON and multipart/form-data for update_profile
@router.put("/me", response_model=APIResponse[ProfileResponse])
async def update_profile(
    full_name: str = Form(None),
    email: str = Form(None),
    profile_picture: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    if email is not None:
        update_data["email"] = email
    if profile_picture is not None:
        if not profile_picture.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            raise HTTPException(status_code=400, detail="Profile picture must be a JPG or PNG file.")
        temp_file_path = f"uploads/{uuid.uuid4()}_{profile_picture.filename}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await profile_picture.read())
        try:
            result = cloudinary.uploader.upload(
                temp_file_path,
                resource_type="image",
                folder="profile_pictures",
            )
            profile_picture_url = result["secure_url"]
            update_data["profile_picture_url"] = profile_picture_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Profile picture upload failed: {str(e)}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    updated = user_repo.update(current_user.id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found.")
    role_repo = RoleRepository(db)
    role = role_repo.get_by_id(updated.role_id)
    response_data = ProfileResponse(
        id=str(updated.id),
        full_name=updated.full_name,
        email=updated.email,
        role=role.name,
        profile_picture_url=updated.profile_picture_url,
    )
    return APIResponse(data=response_data, message="Profile updated successfully.")


@router.patch("/me/change-password", response_model=APIResponse[None])
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

    return APIResponse(data=None, message="Password changed successfully.")
