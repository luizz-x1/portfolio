from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends, Header

SECRET_KEY = ""
ALGORITHM = "HS256"


# Crear token de acceso
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_visitor_token(user_id: int):
    """Token con rol visitante"""
    return create_access_token({"user_id": user_id, "role": "visitor"})


def create_admin_token(user_id: int):
    """Token con rol admin"""
    return create_access_token({"user_id": user_id, "role": "admin"})


def verify_token(token: str):
    """Verifica firma y expiración"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> int:
    """Extrae el ID del usuario del token"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return payload.get("user_id")


def get_current_user(authorization: str = Header(..., alias="Authorization")):
    """Obtiene y valida el usuario desde el header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")

    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload


def require_admin(current_user: dict = Depends(get_current_user)):
    """Permite acceso solo a admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta ruta")
    return current_user


def decodeJWT(token: str):
    """Decodifica sin verificar expiración"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
