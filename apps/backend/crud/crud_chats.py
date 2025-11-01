from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from models.models import Chat, ChatParticipant


# Crear un nuevo chat (puede ser grupal o privado)
def create_chat(db: Session, is_group: bool = False):
    db_chat = Chat(
        is_group=is_group,
        created_at=datetime.now()
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


# Agregar participante a un chat
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


# Obtener todos los chats de un usuario
def get_user_chats(db: Session, user_id: int):
    return (
        db.query(Chat)
        .join(ChatParticipant)
        .filter(ChatParticipant.user_id == user_id)
        .all()
    )


# Obtener un chat por ID
def get_chat_by_id(db: Session, chat_id: int):
    return db.query(Chat).filter(Chat.id == chat_id).first()


# Obtener IDs de los participantes de un chat
def get_chat_participants(db: Session, chat_id: int):
    participants = (
        db.query(ChatParticipant.user_id)
        .filter(ChatParticipant.chat_id == chat_id)
        .all()
    )
    return [p[0] for p in participants]


# Obtener contactos (1 a 1) de un usuario
def get_user_contacts(db: Session, user_id: int):
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


# Buscar chat privado existente entre dos usuarios
def get_private_chat_between_users(db: Session, user1_id: int, user2_id: int):
    return (
        db.query(Chat)
        .join(ChatParticipant)
        .filter(Chat.is_group == False)
        .filter(ChatParticipant.user_id.in_([user1_id, user2_id]))
        .group_by(Chat.id)
        .having(func.count(ChatParticipant.user_id) == 2)
        .first()
    )


# Crear un nuevo chat privado entre dos usuarios
def create_private_chat(db: Session, user1_id: int, user2_id: int):
    new_chat = Chat(
        is_group=False,
        created_at=datetime.now()
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    db.add_all([
        ChatParticipant(chat_id=new_chat.id, user_id=user1_id, joined_at=datetime.now()),
        ChatParticipant(chat_id=new_chat.id, user_id=user2_id, joined_at=datetime.now())
    ])
    db.commit()

    return new_chat
