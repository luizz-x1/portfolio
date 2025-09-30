from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    chat_id: int
    sender_id: int

class MessageResponse(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

class MessageWebSocket(BaseModel):
    type: str = "message"
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime

class ReadReceipt(BaseModel):
    message_id: int
    read_at: datetime

    