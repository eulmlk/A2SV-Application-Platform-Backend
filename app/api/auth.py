from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List  # Important for list responses, though not used in this file

# Import your request schemas
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenRefreshRequest,
)

# Import your RESPONSE schemas - we will use these inside the wrapper
from app.schemas.auth import (
    RegisterResponse,
    TokenResponse,
    AccessTokenResponse,
)

# Import the generic APIResponse wrapper
from app.schemas.base import APIResponse

# Import domain entities and repository interfaces
from app.domain.entities import User as UserEntity  # Renaming to avoid confusion
from app.repositories.sqlalchemy_impl import UserRepository

# Import dependencies and helpers
from app.core.database import get_db
from app.models.role import Role as RoleModel
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)
import uuid
import datetime

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()

@router.post(
    "/register/",
    # The response is an APIResponse containing a single RegisterResponse object
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
        # We will let a custom exception handler format the final JSON
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Get the 'applicant' role from the database
    role = db.query(RoleModel).filter(RoleModel.name == "applicant").first()
    if not role:
        # This is a server configuration error, not a user error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: 'applicant' role not found.",
        )

    # Use your actual domain entity for creation - this is much cleaner
    user_to_create = UserEntity(
        id=uuid.uuid4(),
        email=data.email,
        password=hash_password(data.password),
        full_name=data.full_name,
        role_id=role.id,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )

    # The repository handles the database interaction
    created_user = user_repo.create(user_to_create)

    # Prepare the response data using your Pydantic response schema
    response_data = RegisterResponse(
        id=str(created_user.id),
        full_name=created_user.full_name,
        email=created_user.email,
    )

    # Wrap the data in the standard APIResponse
    return APIResponse(data=response_data, message="User registered successfully.")

@router.post(
    "/token/",
    # The response is an APIResponse containing a TokenResponse
    response_model=APIResponse[TokenResponse],
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Handles user login and token generation.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(data.email)

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},  # Standard for 401
        )

    # Create a single Bearer token
    access_token = create_access_token({"sub": str(user.id)})
    response_data = TokenResponse(access=access_token, refresh=None)  # Now compatible with updated schema

    return APIResponse(data=response_data, message="Login successful.")

@router.post(
    "/token/refresh/",
    # The response is an APIResponse containing an AccessTokenResponse
    response_model=APIResponse[AccessTokenResponse],
)
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Refreshes an access token using a valid Bearer token.
    """
    payload = decode_token(credentials.credentials)

    # Ensure the token is valid with a subject
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user_id = payload["sub"]

    # Create a new access token
    new_access_token = create_access_token({"sub": user_id})

    # Prepare the response data
    response_data = AccessTokenResponse(access=new_access_token)

    return APIResponse(
        data=response_data, message="Access token refreshed successfully."
    )

# Use bearer_scheme as a dependency in protected endpoints
def protected_endpoint(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    # Validate token and proceed (e.g., decode and check expiration)