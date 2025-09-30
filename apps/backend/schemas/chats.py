from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from schemas.users import UserResponse
from schemas.messages import MessageResponse


class ChatBase(BaseModel):
    is_group: bool = False

class ChatCreate(ChatBase):
    pass


class ChatParticipantResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    joined_at: datetime

    user: UserResponse | None = None

    class Config:
        from_attributes = True


class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    participants: List['ChatParticipantResponse'] = []
    messages: List['MessageResponse'] = [] 

    class Config:
        from_attributes = True

class ChatParticipantBase(BaseModel):
    user_id: int

class ChatParticipantCreate(ChatParticipantBase):
    chat_id: int

class ChatParticipantResponse(ChatParticipantBase):
    id: int
    joined_at: datetime

    class Config:
        from_attributes = True