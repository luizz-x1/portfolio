from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.users import UserLogin, Token
from services.auth_service import (
    login_admin,
    verify_access_token_logic,
    refresh_access_token_logic
)

router = APIRouter()


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login para administrador y generación de token JWT."""
    return login_admin(user_data, db)


@router.get("/verify-token")
def verify_access_token(authorization: str = Header(..., alias="Authorization")):
    """Verifica si el token JWT es válido."""
    # Verificar formato correcto del header
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido")

    token = authorization.split(" ")[1]

    payload = verify_access_token_logic(token)

    return {"valid": True, "user_id": payload["user_id"], "role": payload["role"]}


@router.post("/refresh-token", response_model=Token)
def refresh_access_token(authorization: str = Header(..., alias="Authorization")):
    """Genera un nuevo token a partir de uno expirado."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de token inválido")

    token = authorization.split(" ")[1]

    return refresh_access_token_logic(token)
