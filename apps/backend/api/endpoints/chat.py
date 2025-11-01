from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from schemas.chats import ChatResponse
from schemas.messages import MessageCreate, MessageResponse
from utils.security import get_current_user
from services.chat_service import (
    create_or_get_chat,
    get_user_chats,
    create_and_send_message,
    get_chat_messages
)

router = APIRouter()


@router.post("/chats/{receiver_id}", response_model=ChatResponse)
def create_or_get_private_chat(
    receiver_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crea o recupera un chat privado entre dos usuarios."""
    return create_or_get_chat(db, current_user["user_id"], receiver_id)


@router.get("/users/{user_id}/chats", response_model=List[ChatResponse])
def get_chats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene todos los chats del usuario."""
    return get_user_chats(db, user_id)


@router.post("/messages/", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crea un mensaje y lo envía a los participantes del chat."""
    return await create_and_send_message(db, message, current_user["user_id"])


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
def get_messages(
    chat_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene los mensajes de un chat."""
    return get_chat_messages(db, chat_id, skip, limit)
