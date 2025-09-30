from sqlalchemy.orm import Session
from models.models import User, Chat, ChatParticipant
from schemas.users import UserCreate, UserUpdate
from datetime import datetime
import uuid

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_unique_id(db: Session, unique_id: str):
    return db.query(User).filter(User.unique_id == unique_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_anonymous_user(db: Session):
    # Crear usuario
    unique_id = f"visitor_{uuid.uuid4()}"
    db_user = User(
        unique_id=unique_id,
        name="Visitor",
        role="visitor",
        create_at=datetime.now(),
        last_connection=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Crear chat para el usuario
    db_chat = Chat(
        is_group=False,
        created_at=datetime.now()
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    
    # Agregar usuario al chat como participante
    db_participant = ChatParticipant(
        chat_id=db_chat.id,
        user_id=db_user.id,
        joined_at=datetime.now()
    )
    db.add(db_participant)
    db.commit()
    
    # Agregar adm al usuario
    admin_user = db.query(User).filter(User.role == "admin").first()
    if admin_user:
        admin_participant = ChatParticipant(
            chat_id=db_chat.id,
            user_id=admin_user.id,
            joined_at=datetime.now()
        )
        db.add(admin_participant)
        db.commit()
    
    return db_user

def update_user_name(db: Session, user_id: int, name: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.name = name
        db_user.last_connection = datetime.now()
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_last_connection(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.last_connection = datetime.now()
        db.commit()
    return db_user

def get_admin_users(db: Session):
    return db.query(User).filter(User.role == "admin").all()