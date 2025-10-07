from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from schemas.users import UserResponse, UserUpdateName, UserWithToken
from crud import crud_users
from utils.security import create_visitor_token, get_current_user, require_admin

router = APIRouter()

@router.post("/users/anon", response_model=UserWithToken)
def create_anonymous_user(db: Session = Depends(get_db)):
    db_user = crud_users.create_anonymous_user(db)
    access_token = create_visitor_token(db_user.id)
    
    return {
        "unique_id": db_user.unique_id,
        "name": db_user.name,
        "create_at": db_user.create_at,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtener usuario por ID (requiere autenticación)"""
    db_user = crud_users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.patch("/users/{user_id}/name", response_model=UserResponse)
def update_user_name(
    user_id: int,
    name_data: UserUpdateName,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualizar nombre (usuario autenticado)"""
    return crud_users.update_user_name(db, user_id=user_id, name=name_data.name)

@router.get("/users/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Obtener lista de usuarios (solo admin)"""
    return crud_users.get_users(db, skip=skip, limit=limit)