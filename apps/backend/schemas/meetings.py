from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from schemas.users import UserResponse

class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_link: Optional[str] = None
    scheduled_at: datetime
    status: str = "pending"

class MeetingCreate(MeetingBase):
    chat_id: int
    organizer_id: int

class MeetingResponse(MeetingBase):
    id: int
    chat_id: int
    organizer_id: int
    created_at: datetime
    participants: List[UserResponse] = []

    class Config:
        from_attributes = True

class MeetingParticipantBase(BaseModel):
    user_id: int
    response: Optional[str] = "pending"

class MeetingParticipantCreate(MeetingParticipantBase):
    meeting_id: int

class MeetingParticipantResponse(MeetingParticipantBase):
    id: int
    responded_at: Optional[datetime]

    class Config:
        from_attributes = True

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_link: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None