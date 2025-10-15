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
    """Retorna los chats en los que participa el usuario."""
    return (
        db.query(Chat)
        .join(ChatParticipant)
        .filter(ChatParticipant.user_id == user_id)
        .all()
    )


def get_chat_by_id(db: Session, chat_id: int):
    """Retorna un chat por su ID."""
    return db.query(Chat).filter(Chat.id == chat_id).first()


def get_chat_participants(db: Session, chat_id: int):
    """Retorna los IDs de todos los participantes de un chat específico."""
    participants = (
        db.query(ChatParticipant.user_id)
        .filter(ChatParticipant.chat_id == chat_id)
        .all()
    )
    return [p[0] for p in participants]


def get_user_contacts(db: Session, user_id: int):
    """
    Retorna los IDs de los usuarios con los que el usuario tiene chats directos.
    """
    subquery = (
        db.query(ChatParticipant.chat_id)
        .join(Chat)
        .filter(ChatParticipant.user_id == user_id, Chat.is_group == False)
        .subquery()
    )

    contacts = (
        db.query(ChatParticipant.user_id)
        .filter(ChatParticipant.chat_id.in_(subquery))
        .filter(ChatParticipant.user_id != user_id)
        .distinct()
        .all()
    )

    return [c[0] for c in contacts]