from sqlalchemy.orm import Session
from models.models import Message, ChatParticipant, Chat
from schemas.messages import MessageCreate
from datetime import datetime


# Crear un nuevo mensaje
def create_message(db: Session, message: MessageCreate):
    db_message = Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        content=message.content,
        created_at=datetime.now(),
        status="send"
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


# Obtener los mensajes de un chat
def get_chat_messages(db: Session, chat_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


# Marcar mensaje como leído
def mark_message_as_read(db: Session, message_id: int):
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db_message.is_read = True
        db_message.read_at = datetime.now()
        db.commit()
        db.refresh(db_message)
    return db_message


# Obtener mensajes no leídos en un chat
def get_unread_messages(db: Session, user_id: int, chat_id: int):
    return (
        db.query(Message)
        .filter(
            Message.chat_id == chat_id,
            Message.sender_id != user_id,
            Message.is_read == False
        )
        .all()
    )


# Obtener mensajes pendientes (no entregados)
def get_pending_messages(db: Session, user_id: int):
    chat_ids = db.query(ChatParticipant.chat_id).filter(ChatParticipant.user_id == user_id)
    
    return (
        db.query(Message)
        .filter(Message.chat_id.in_(chat_ids))
        .filter(Message.sender_id != user_id)
        .filter(Message.status != "delivered")
        .order_by(Message.created_at.asc())
        .all()
    )


# Actualizar estado de un mensaje (send, delivered, read)
async def update_status(db: Session, message_id: int, status: str):
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db_message.status = status
        if status == "read":
            db_message.read_at = datetime.now()
        elif status == "delivered":
            db_message.delivered_at = datetime.now()
        db.commit()
        db.refresh(db_message)
    return db_message


# Obtener contactos con los que el usuario ha tenido chats
def get_contacts_for_user(db: Session, user_id: int):
    """
    Devuelve los IDs de los contactos con los que el usuario ha tenido conversaciones.
    """
    chats = (
        db.query(ChatParticipant.chat_id)
        .filter(ChatParticipant.user_id == user_id)
        .subquery()
    )

    participants = (
        db.query(ChatParticipant.user_id)
        .filter(ChatParticipant.chat_id.in_(chats))
        .filter(ChatParticipant.user_id != user_id)
        .distinct()
        .all()
    )

    return [p[0] for p in participants]
