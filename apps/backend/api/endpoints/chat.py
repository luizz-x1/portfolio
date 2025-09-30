from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from schemas.chats import ChatResponse, ChatCreate
from schemas.messages import MessageCreate, MessageResponse
from crud import crud_chats, crud_messages

router = APIRouter()

@router.post("/chats/{chat_id}/participants/{user_id}")
def add_participant(chat_id: int, user_id: int, db: Session = Depends(get_db)):
    """Agregar participante a chat"""
    return crud_chats.add_participant_to_chat(db, chat_id=chat_id, user_id=user_id)

@router.get("/users/{user_id}/chats", response_model=List[ChatResponse])
def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    """Obtener chats de un usuario"""
    return crud_chats.get_user_chats(db, user_id=user_id)

@router.post("/messages/", response_model=MessageResponse)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Crear nuevo mensaje"""
    return crud_messages.create_message(db, message=message)

@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(chat_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener mensajes de un chat"""
    return crud_messages.get_chat_messages(db, chat_id=chat_id, skip=skip, limit=limit)