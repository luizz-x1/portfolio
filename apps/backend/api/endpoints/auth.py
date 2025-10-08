from fastapi import APIRouter, Depends, HTTPException, Header
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

@router.get("/verify-token")
def verify_access_token(authorization: str = Header(..., alias="Authorization")):
    """Verificar si el token JWT es válido"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido")

    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    return {"valid": True, "user_id": payload["user_id"], "role": payload["role"]}

@router.post("/refresh-token", response_model=Token)
def refresh_access_token(authorization: str = Header(..., alias="Authorization")):
    """Generar un nuevo token a partir de uno válido"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido")

    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    new_token = create_access_token({
        "user_id": payload["user_id"],
        "role": payload["role"]
    })

    return {"access_token": new_token, "token_type": "bearer"}
