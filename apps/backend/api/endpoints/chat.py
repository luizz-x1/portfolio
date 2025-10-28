from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from config.database import get_db
from schemas.chats import ChatResponse
from schemas.messages import MessageCreate, MessageResponse
from crud import crud_chats, crud_messages
from utils.security import get_current_user
# from ws_manager import send_message_to_user
from utils.redis import publish
router = APIRouter()

@router.post("/chats/{receiver_id}", response_model=ChatResponse)
def create_or_get_private_chat(
    receiver_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea un chat 1 a 1 entre el usuario autenticado y el receptor indicado.
    Si ya existe, lo devuelve sin duplicarlo.
    """
    
    sender_id = current_user['user_id']

    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="No puedes crear un chat contigo mismo")

    existing_chat = crud_chats.get_private_chat_between_users(db, sender_id, receiver_id)
    if existing_chat:
        return existing_chat

    new_chat = crud_chats.create_private_chat(db, sender_id, receiver_id)
    return new_chat


@router.get("/users/{user_id}/chats", response_model=List[ChatResponse])
def get_user_chats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtener todos los chats (1 a 1) de un usuario"""
    return crud_chats.get_user_chats(db, user_id=user_id)


@router.post("/messages/", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear nuevo mensaje en un chat existente y notificar en tiempo real.
    """
    new_message = crud_messages.create_message(db, message=message)

    sender_id = current_user["user_id"]

    participants = crud_chats.get_chat_participants(db, message.chat_id)

    message_data = {
        "type": "message",
        "chat_id": message.chat_id,
        "from": sender_id,
        "content": message.content,
    }

    for user_id in participants:
        if user_id != sender_id:

            await publish(f"user:{user_id}", json.dumps(message_data))

    return new_message


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(
    chat_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtener los mensajes de un chat (1 a 1)"""
    return crud_messages.get_chat_messages(db, chat_id=chat_id, skip=skip, limit=limit)
