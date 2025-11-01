from fastapi import HTTPException
from sqlalchemy.orm import Session
from jose import JWTError
from utils.security import create_access_token, verify_token, decodeJWT
from schemas.users import UserLogin, Token
from crud.crud_auth import get_user_by_email


def login_admin(user_data: UserLogin, db: Session) -> Token:
    """Login de administrador y creación del token."""
    user = get_user_by_email(db, user_data.email)

    if not user or user.role != "admin":
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token({"user_id": user.id, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


def verify_access_token_logic(token: str):
    """Verifica si el token es válido."""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload


def refresh_access_token_logic(token: str) -> Token:
    """Genera un nuevo token a partir de uno expirado."""
    payload = verify_token(token)
    if payload:
        raise HTTPException(status_code=400, detail="El token aún es válido")

    try:
        expired_payload = decodeJWT(token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido")

    new_token = create_access_token({
        "user_id": expired_payload["user_id"],
        "role": expired_payload["role"]
    })

    return {"access_token": new_token, "token_type": "bearer"}
