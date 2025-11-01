from sqlalchemy.orm import Session
from models.models import User, Chat, ChatParticipant
from datetime import datetime
import uuid


def get_user(db: Session, user_id: int):
    """Obtiene un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_unique_id(db: Session, unique_id: str):
    """Busca un usuario por su unique_id."""
    return db.query(User).filter(User.unique_id == unique_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve todos los usuarios con paginación."""
    return db.query(User).offset(skip).limit(limit).all()


def create_anonymous_user(db: Session):
    """Crea un usuario visitante y su chat con el admin."""
    # Crear usuario anónimo
    unique_id = f"visitor_{uuid.uuid4()}"
    user = User(
        unique_id=unique_id,
        name="Visitor",
        role="visitor",
        create_at=datetime.now(),
        last_connection=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Crear chat individual
    chat = Chat(is_group=False, created_at=datetime.now())
    db.add(chat)
    db.commit()
    db.refresh(chat)

    # Agregar visitante al chat
    db.add(ChatParticipant(chat_id=chat.id, user_id=user.id, joined_at=datetime.now()))
    db.commit()

    # Agregar admin al mismo chat
    admin = db.query(User).filter(User.role == "admin").first()
    if admin:
        db.add(ChatParticipant(chat_id=chat.id, user_id=admin.id, joined_at=datetime.now()))
        db.commit()

    return user


def update_user_name(db: Session, user_id: int, name: str):
    """Actualiza el nombre del usuario."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.last_connection = datetime.now()
        db.commit()
        db.refresh(user)
    return user


def update_user_last_connection(db: Session, user_id: int):
    """Actualiza la fecha de última conexión."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_connection = datetime.now()
        db.commit()
    return user


def get_admin_users(db: Session):
    """Devuelve todos los usuarios con rol admin."""
    return db.query(User).filter(User.role == "admin").all()
