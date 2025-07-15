from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, TokenRefreshRequest, AccessTokenResponse
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import UserRepository
from app.models.role import Role as RoleModel
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/", response_model=RegisterResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    # Check if user exists
    if user_repo.get_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered.")
    # Get Applicant role (assume id=1 or fetch by name)
    role = db.query(RoleModel).filter(RoleModel.name == "Applicant").first()
    if not role:
        raise HTTPException(status_code=500, detail="Applicant role not found.")
    user_id = uuid.uuid4()
    hashed_pw = hash_password(data.password)
    user = user_repo.create(
        type('User', (), {
            'id': user_id,
            'email': data.email,
            'password': hashed_pw,
            'full_name': data.full_name,
            'role_id': role.id,
            'created_at': None,
            'updated_at': None
        })()
    )
    return RegisterResponse(id=str(user.id), full_name=user.full_name, email=user.email)

@router.post("/token/", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access=access, refresh=refresh)

@router.post("/token/refresh/", response_model=AccessTokenResponse)
def refresh_token(data: TokenRefreshRequest):
    payload = decode_token(data.refresh)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")
    user_id = payload["sub"]
    access = create_access_token({"sub": user_id})
    return AccessTokenResponse(access=access) 