from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends, Header

SECRET_KEY = ""
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_visitor_token(user_id: int):
    """Crear token específico para visitantes"""
    return create_access_token({"user_id": user_id, "role": "visitor"})

def create_admin_token(user_id: int):
    """Crear token específico para admin"""
    return create_access_token({"user_id": user_id, "role": "admin"})

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_id_from_token(token: str) -> int:
    """Extraer user_id del token"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return payload.get("user_id")

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(authorization: str = Header(..., alias="Authorization")):
    """Valida el token desde el header Authorization: Bearer <token>"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload

def require_admin(current_user: dict = Depends(get_current_user)):
    """Permite solo usuarios con rol admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta ruta")
    return current_user
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1NCwicm9sZSI6InZpc2l0b3IiLCJleHAiOjE3NTk5NTIwOTd9.O-Oru2qzu57-moTiGvkdWj5gfIjI3LgP9ZNkLBHYchA