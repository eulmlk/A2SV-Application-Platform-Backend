from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access: str
    refresh: str | None = None  # Made refresh optional with a default of None

class TokenRefreshRequest(BaseModel):
    refresh: str

class AccessTokenResponse(BaseModel):
    access: str

# Profile management schemas
class ProfileResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: str

class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str