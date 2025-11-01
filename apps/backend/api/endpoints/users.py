from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from schemas.users import UserResponse, UserUpdateName, UserWithToken
from utils.security import get_current_user, require_admin
from services import user_service

router = APIRouter()


# --- Crear usuario anónimo ---
@router.post("/users/anon", response_model=UserWithToken)
def create_anonymous_user(db: Session = Depends(get_db)):
    """Crea un usuario visitante y retorna su token."""
    return user_service.create_anonymous_user_service(db)


# --- Obtener usuario por ID ---
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene un usuario """
    return user_service.get_user_service(db, user_id)


# --- Actualizar nombre del usuario ---
@router.patch("/users/{user_id}/name", response_model=UserResponse)
def update_user_name(
    user_id: int,
    name_data: UserUpdateName,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualiza el nombre del usuario autenticado."""
    return user_service.update_user_name_service(db, user_id, name_data)


# --- Listar usuarios (solo admin) ---
@router.get("/users/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Devuelve todos los usuarios (solo para administradores)."""
    return user_service.get_users_service(db, skip, limit)
