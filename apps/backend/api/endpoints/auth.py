from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from schemas.users import UserLogin, Token
from models.models import User
from utils.security import create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login para admin"""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}