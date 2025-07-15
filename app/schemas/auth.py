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
    refresh: str

class TokenRefreshRequest(BaseModel):
    refresh: str

class AccessTokenResponse(BaseModel):
    access: str 