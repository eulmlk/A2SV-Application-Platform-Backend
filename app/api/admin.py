from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.admin import (
    AdminCreateUserRequest,
    AdminUserResponse,
    AdminCycleCreateRequest,
    AdminCycleResponse,
    AdminUpdateUserRequest,
    AdminUpdateCycleRequest,
    AdminListUsersResponse,
)
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import (
    UserRepository,
    RoleRepository,
    ApplicationCycleRepository,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    require_token_type,
)
from app.api.deps import admin_required
from app.domain.entities import User, ApplicationCycle
from app.schemas.auth import TokenResponse
from app.schemas.base import APIResponse
from app.core.utils import (
    raise_not_found,
    raise_forbidden,
    raise_conflict,
    raise_validation_error,
    raise_internal_error,
)
from app.schemas.auth import LoginRequest
import uuid
from datetime import datetime, timezone
from fastapi.security import HTTPAuthorizationCredentials
from app.api.auth import bearer_scheme


def get_access_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return require_token_type(credentials.credentials, "access")


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/users/{user_id}/",
    response_model=APIResponse[AdminUserResponse],
    dependencies=[Depends(bearer_scheme)],
)
def get_user_by_id(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise_validation_error("Invalid user ID format.")

    user = user_repo.get_by_id(user_uuid)
    if not user:
        raise_not_found("User not found.", "user")
    role = role_repo.get_by_id(user.role_id) if user.role_id else None
    role_name = role.name if role else ""

    response_data = AdminUserResponse(
        id=str(user.id), full_name=user.full_name, email=user.email, role=role_name
    )

    return APIResponse(data=response_data, message="User retrieved successfully.")


@router.post("/login/", response_model=APIResponse[TokenResponse])
def admin_login(data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email
    password = data.password
    if not email or not password:
        raise_validation_error("Email and password required.")
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    user = user_repo.get_by_email(email)
    if not user or not verify_password(password, user.password):
        raise_forbidden("Incorrect email or password.")
    if user.role_id != 4:  # Only allow admin login
        raise_forbidden("Admin access required.")
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    role = role_repo.get_by_id(user.role_id) if user.role_id else None
    role_name = role.name if role else ""
    response_data = TokenResponse(access=access, refresh=refresh, role=role_name)
    return APIResponse(data=response_data, message="Login successful.")


@router.post(
    "/users/",
    response_model=APIResponse[AdminUserResponse],
    status_code=201,
    dependencies=[Depends(bearer_scheme)],
)
def create_user(
    data: AdminCreateUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    if user_repo.get_by_email(data.email):
        raise_conflict("Email already registered.")
    role = role_repo.get_by_name(data.role)
    if not role:
        raise_not_found("Role not found.", "role")
    user = User(
        id=uuid.uuid4(),
        email=data.email,
        password=hash_password(data.password),
        full_name=data.full_name,
        role_id=role.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    created = user_repo.create(user)
    response_data = AdminUserResponse(
        id=str(created.id),
        full_name=created.full_name,
        email=created.email,
        role=role.name,
    )
    return APIResponse(data=response_data, message="User created successfully.")


@router.get(
    "/users/",
    response_model=APIResponse[AdminListUsersResponse],
    dependencies=[Depends(bearer_scheme)],
)
def list_users(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(
        10, ge=1, le=100, description="Number of users per page (max 100)"
    ),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    get_access_token_payload(credentials)
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    offset = (page - 1) * limit
    users = user_repo.list_all(offset=offset, limit=limit)
    roles = {r.id: r.name for r in role_repo.list_all()}
    response_items = [
        AdminUserResponse(
            id=str(u.id),
            full_name=u.full_name,
            email=u.email,
            role=roles.get(u.role_id, ""),
        )
        for u in users
    ]
    # Get total count for pagination
    total_count = user_repo.count_all()
    response_data = AdminListUsersResponse(
        users=response_items,
        total_count=total_count,
        page=page,
        limit=limit,
    )
    return APIResponse(data=response_data, message="Users retrieved successfully.")


@router.put(
    "/users/{user_id}/",
    response_model=APIResponse[AdminUserResponse],
    dependencies=[Depends(bearer_scheme)],
)
def update_user(
    user_id: str,
    data: AdminUpdateUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise_validation_error("Invalid user ID format.")
    update_data = {}
    if data.full_name is not None:
        update_data["full_name"] = data.full_name
    if data.email is not None:
        update_data["email"] = data.email
    if data.password is not None:
        update_data["password"] = hash_password(data.password)
    if data.role is not None:
        role = role_repo.get_by_name(data.role)
        if not role:
            raise_not_found("Role not found.", "role")
        update_data["role_id"] = role.id
    updated = user_repo.update(user_uuid, **update_data)
    if not updated:
        raise_not_found("User not found.", "user")
    role = role_repo.get_by_id(updated.role_id) if updated.role_id else None
    role_name = role.name if role else ""
    response_data = AdminUserResponse(
        id=str(updated.id),
        full_name=updated.full_name,
        email=updated.email,
        role=role_name,
        profile_picture=updated.profile_picture,
    )
    return APIResponse(data=response_data, message="User updated successfully.")


@router.delete(
    "/users/{user_id}/",
    response_model=APIResponse[AdminUserResponse],
    dependencies=[Depends(bearer_scheme)],
)
def delete_user(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    user_repo = UserRepository(db)
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise_validation_error("Invalid user ID format.")
    deleted = user_repo.delete(user_uuid)
    if not deleted:
        raise_not_found("User not found.", "user")
    return APIResponse(message="User deleted successfully.")


@router.post(
    "/cycles/",
    response_model=APIResponse[AdminCycleResponse],
    status_code=201,
    dependencies=[Depends(bearer_scheme)],
)
def create_cycle(
    data: AdminCycleCreateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    cycle_repo = ApplicationCycleRepository(db)
    if cycle_repo.get_by_name(data.name):
        raise_conflict("Cycle with this name already exists.")
    if data.start_date >= data.end_date:
        raise_validation_error("Start date must be before end date.")
    cycle = ApplicationCycle(
        id=0,  # Use 0 as a placeholder; DB will assign the real id
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        is_active=False,
        created_at=datetime.now(timezone.utc),
        description=data.description if data.description else None,
    )
    created = cycle_repo.create(cycle)
    response_data = AdminCycleResponse(
        id=created.id,
        name=created.name,
        start_date=created.start_date,
        end_date=created.end_date,
        is_active=created.is_active,
        created_at=created.created_at,
        description=created.description if created.description else None,
    )
    return APIResponse(data=response_data, message="Cycle created successfully.")


@router.patch(
    "/cycles/{cycle_id}/activate/",
    response_model=APIResponse[AdminCycleResponse],
    dependencies=[Depends(bearer_scheme)],
)
def activate_cycle(
    cycle_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    cycle_repo = ApplicationCycleRepository(db)
    activated = cycle_repo.activate(cycle_id)
    if not activated:
        raise_not_found("Cycle not found.", "cycle")
    return APIResponse(data=activated, message=f"Cycle {activated.name} is now active.")


@router.put(
    "/cycles/{cycle_id}/",
    response_model=APIResponse[AdminCycleResponse],
    dependencies=[Depends(bearer_scheme)],
)
def update_cycle(
    cycle_id: int,
    data: AdminUpdateCycleRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    cycle_repo = ApplicationCycleRepository(db)
    existing_cycle = cycle_repo.get_by_id(cycle_id)
    if not existing_cycle:
        raise_not_found("Cycle not found.", "cycle")
    if data.name is not None:
        cycle_with_name = cycle_repo.get_by_name(data.name)
        if cycle_with_name and cycle_with_name.id != cycle_id:
            raise_conflict("Cycle with this name already exists.")
    if data.start_date is not None and data.end_date is not None:
        if data.start_date >= data.end_date:
            raise_validation_error("Start date must be before end date.")
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    updated = cycle_repo.update(cycle_id, **update_data)
    if not updated:
        raise_not_found("Cycle not found.", "cycle")
    response_data = AdminCycleResponse(
        id=updated.id,
        name=updated.name,
        start_date=updated.start_date,
        end_date=updated.end_date,
        is_active=updated.is_active,
        created_at=updated.created_at,
        description=updated.description if updated.description else None,
    )
    return APIResponse(data=response_data, message="Cycle updated successfully.")


@router.delete(
    "/cycles/{cycle_id}/",
    response_model=APIResponse[AdminCycleResponse],
    dependencies=[Depends(bearer_scheme)],
)
def delete_cycle(
    cycle_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(admin_required),
    db: Session = Depends(get_db),
):
    get_access_token_payload(credentials)
    cycle_repo = ApplicationCycleRepository(db)
    deleted = cycle_repo.delete(cycle_id)
    if not deleted:
        raise_not_found("Cycle not found.", "cycle")
    return APIResponse(message="Cycle deleted successfully.")
