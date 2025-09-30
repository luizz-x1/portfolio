from sqlalchemy.orm import Session
from models.models import Message
from schemas.messages import MessageCreate
from datetime import datetime

def create_message(db: Session, message: MessageCreate):
    db_message = Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        content=message.content,
        created_at=datetime.now(),
        is_read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, chat_id: int, skip: int = 0, limit: int = 100):
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).offset(skip).limit(limit).all()

def mark_message_as_read(db: Session, message_id: int):
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db_message.is_read = True
        db_message.read_at = datetime.now()
        db.commit()
        db.refresh(db_message)
    return db_message

def get_unread_messages(db: Session, user_id: int, chat_id: int):
    return db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.sender_id != user_id,
        Message.is_read == False
    ).all()