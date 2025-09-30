from sqlalchemy.orm import Session
from models.models import Chat, ChatParticipant
from datetime import datetime

def create_chat(db: Session, is_group: bool = False):
    db_chat = Chat(
        is_group=is_group,
        created_at=datetime.now()
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def add_participant_to_chat(db: Session, chat_id: int, user_id: int):
    db_participant = ChatParticipant(
        chat_id=chat_id,
        user_id=user_id,
        joined_at=datetime.now()
    )
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant

def get_user_chats(db: Session, user_id: int):
    return db.query(Chat).join(ChatParticipant).filter(ChatParticipant.user_id == user_id).all()

def get_chat_by_id(db: Session, chat_id: int):
    return db.query(Chat).filter(Chat.id == chat_id).first()