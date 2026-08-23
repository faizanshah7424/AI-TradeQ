from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class PermissionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_locked: bool
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True
