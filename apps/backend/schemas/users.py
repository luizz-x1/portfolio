from pydantic import BaseModel
from datetime import datetime
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from schemas.chats import ChatResponse

class UserBase(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = "visitor"

class UserCreate(UserBase):
    unique_id: str
    create_at: datetime

class UserCreateAdmin(UserBase):
    email: str
    name: str
    role: str = "admin"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserUpdateName(BaseModel):
    name: str

class UserResponse(UserBase):
    id: int
    unique_id: str
    create_at: datetime
    last_connection: Optional[datetime]

    class Config:
        from_attributes = True

class UserWithChats(UserResponse):
    
    chats: list['ChatResponse'] = [] 

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    role: str

class UserWithToken(BaseModel):
    id: int
    unique_id: str
    name: Optional[str] = None
    role: str
    create_at: datetime
    last_connection: Optional[datetime]
    access_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True