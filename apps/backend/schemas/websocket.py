from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class WebSocketMessage(BaseModel):
    type: str  # message, user_joined, user_left, typing, read_receipt
    data: Optional[Any] = None
    user_id: Optional[int] = None
    timestamp: datetime

class UserStatusUpdate(BaseModel):
    user_id: int
    status: str  # online, offline, away
    last_connection: datetime

class TypingIndicator(BaseModel):
    chat_id: int
    user_id: int
    is_typing: bool

class ConnectionInfo(BaseModel):
    user_id: int
    role: str
    status: str