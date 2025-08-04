from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
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
)
from app.core.utils import raise_conflict, raise_internal_error, raise_unauthorized
import uuid
import datetime

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


@router.post(
    "/register/",
    response_model=APIResponse[RegisterResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Handles user registration.
    """
    user_repo = UserRepository(db)

    # Check if user exists
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
    """
    Handles user login and token generation.
    """
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user = user_repo.get_by_email(data.email)
    role = role_repo.get_by_id(user.role_id)

    if not user or not verify_password(data.password, user.password):
        raise_unauthorized("Incorrect email or password.")

    # Create both access and refresh tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response_data = TokenResponse(access=access_token, refresh=refresh_token, role=role.name)

    return APIResponse(data=response_data, message="Login successful.")


@router.post(
    "/token/refresh/",
    response_model=APIResponse[AccessTokenResponse],
)
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Refreshes an access token using a valid Bearer token.
    """
    payload = require_token_type(credentials.credentials, "refresh")

    # Ensure the token is valid with a subject
    if payload is None or "sub" not in payload:
        raise_unauthorized("Invalid or expired token.")

    user_id = payload["sub"]

    # Create a new access token
    new_access_token = create_access_token({"sub": user_id})

    # Prepare the response data
    response_data = AccessTokenResponse(access=new_access_token)

    return APIResponse(
        data=response_data, message="Access token refreshed successfully."
    )


# Use bearer_scheme as a dependency in protected endpoints
def protected_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    payload = require_token_type(credentials.credentials, "access")
    # Validate token and proceed (e.g., decode and check expiration)
