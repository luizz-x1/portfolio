from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud import crud_users
from utils.security import create_visitor_token
from schemas.users import UserUpdateName

def create_anonymous_user_service(db: Session):
    """Crea un usuario anónimo y genera su token."""
    user = crud_users.create_anonymous_user(db)
    token = create_visitor_token(user.id)

    return {
        "id": user.id,
        "unique_id": user.unique_id,
        "name": user.name,
        "create_at": user.create_at,
        "access_token": token,
        "token_type": "bearer"
    }

def get_user_service(db: Session, user_id: int):
    """Obtiene un usuario por ID."""
    user = crud_users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user_name_service(db: Session, user_id: int, name_data: UserUpdateName):
    """Actualiza el nombre de un usuario."""
    return crud_users.update_user_name(db, user_id=user_id, name=name_data.name)

def get_users_service(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene la lista de usuarios (solo admin)."""
    return crud_users.get_users(db, skip=skip, limit=limit)
