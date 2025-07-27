from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.security import decode_token, require_token_type
from app.core.database import get_db
from app.repositories.sqlalchemy_impl import UserRepository
from app.models.user import User as UserModel
from app.domain.entities import User
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token/")

# Dependency to get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = require_token_type(token, "access")
    if payload is None or "sub" not in payload:
        raise credentials_exception
    user_id = payload["sub"]
    try:
        user_uuid = uuid.UUID(user_id)
    except Exception:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_uuid)
    if user is None:
        raise credentials_exception
    return user

# Applicant RBAC guard
def applicant_required(current_user: User = Depends(get_current_user)):
    # Assume role_id 1 is Applicant, or check by role name if needed
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Applicant access required.")
    return current_user

def admin_required(current_user: User = Depends(get_current_user)):
    # Check by role_id or fetch role name if needed
    if current_user.role_id != 4:  # Adjust if your admin role_id is different
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user

def reviewer_required(current_user: User = Depends(get_current_user)):
    if current_user.role_id != 2:  # Adjust if reviewer role_id is different
        raise HTTPException(status_code=403, detail="Reviewer access required.")
    return current_user 

def manager_required(current_user: User = Depends(get_current_user)):
    if current_user.role_id != 3 and current_user.role_id != 4:
        raise HTTPException(status_code=403, detail="Manager or Admin access required.")
    return current_user
