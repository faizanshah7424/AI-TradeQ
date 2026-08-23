from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Plaintext user password complying with policy")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., description="User password")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid unrevoked refresh token")

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Existing current password")
    new_password: str = Field(..., min_length=8, description="New password complying with policy")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token lifetime in seconds")

class MessageResponse(BaseModel):
    message: str
    status: str = "success"
