from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,  # New Import
    ResetPasswordRequest,  # New Import
)

from app.schemas.auth import (
    RegisterResponse,
    TokenResponse,
    AccessTokenResponse,
)

from app.schemas.base import APIResponse

from app.domain.entities import User as UserEntity
from app.repositories.sqlalchemy_impl import RoleRepository, UserRepository

from app.core.database import get_db
from app.models.role import Role as RoleModel
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    require_token_type,
    create_refresh_token,
    create_password_reset_token,  # New Import
)
from app.core.utils import (
    raise_conflict,
    raise_internal_error,
    raise_unauthorized,
    raise_not_found,
)
import uuid
import datetime
from app.core.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


@router.post(
    "/register/",
    response_model=APIResponse[RegisterResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # ... existing register code ...
    user_repo = UserRepository(db)
    if user_repo.get_by_email(data.email):
        raise_conflict("An account with this email already exists.")
    role = db.query(RoleModel).filter(RoleModel.name == "applicant").first()
    if not role:
        raise_internal_error("Server configuration error: 'applicant' role not found.")
    user_to_create = UserEntity(
        id=uuid.uuid4(),
        email=data.email,
        password=hash_password(data.password),
        full_name=data.full_name,
        role_id=role.id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    created_user = user_repo.create(user_to_create)
    response_data = RegisterResponse(
        id=str(created_user.id),
        full_name=created_user.full_name,
        email=created_user.email,
    )
    return APIResponse(data=response_data, message="User registered successfully.")


@router.post(
    "/token/",
    response_model=APIResponse[TokenResponse],
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # ... existing login code ...
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user = user_repo.get_by_email(data.email)
    if not user or not verify_password(data.password, user.password):
        raise_unauthorized("Incorrect email or password.")
    role = role_repo.get_by_id(user.role_id)
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    response_data = TokenResponse(
        access=access_token, refresh=refresh_token, role=role.name
    )
    return APIResponse(data=response_data, message="Login successful.")


# --- NEW FORGOT PASSWORD ENDPOINT ---
@router.post("/forgot-password/", response_model=APIResponse)
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Handles the request to reset a password.
    Sends a reset link to the user's email if the account exists.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(data.email)

    # To prevent email enumeration attacks, always return a success response.
    # The email is only sent if the user actually exists.
    if user:
        reset_token = create_password_reset_token({"sub": str(user.id)})
        await send_password_reset_email(
            email_to=user.email, callback_url=data.callback_url, token=reset_token
        )

    return APIResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


# --- NEW RESET PASSWORD ENDPOINT ---
@router.post("/reset-password/", response_model=APIResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Resets the user's password using a valid token.
    """
    # Validate the token is a valid 'password_reset' token
    payload = require_token_type(data.token, "password_reset")

    try:
        user_uuid = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        raise_unauthorized("Invalid token payload.")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_uuid)

    if not user:
        raise_not_found("User not found.", "user")

    # Update the user's password
    hashed_new_password = hash_password(data.new_password)
    updated_user = user_repo.update(user_uuid, password=hashed_new_password)

    if not updated_user:
        raise_internal_error("Failed to update password.")

    return APIResponse(message="Your password has been successfully reset.")


@router.post(
    "/token/refresh/",
    response_model=APIResponse[AccessTokenResponse],
)
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # ... existing refresh token code ...
    payload = require_token_type(credentials.credentials, "refresh")
    if payload is None or "sub" not in payload:
        raise_unauthorized("Invalid or expired token.")
    user_id = payload["sub"]
    new_access_token = create_access_token({"sub": user_id})
    response_data = AccessTokenResponse(access=new_access_token)
    return APIResponse(
        data=response_data, message="Access token refreshed successfully."
    )
