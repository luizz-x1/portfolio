from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends, Header

SECRET_KEY = ""
ALGORITHM = "HS256"


# Crear token de acceso general
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Crear token con rol visitante
def create_visitor_token(user_id: int):
    return create_access_token({"user_id": user_id, "role": "visitor"})


# Crear token con rol administrador
def create_admin_token(user_id: int):
    return create_access_token({"user_id": user_id, "role": "admin"})


# Verificar si un token es válido y no ha expirado
def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# Obtener el user_id contenido en el token
def get_user_id_from_token(token: str) -> int:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return payload.get("user_id")


# Extraer y validar token desde los headers HTTP
def get_current_user(authorization: str = Header(..., alias="Authorization")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")

    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload


# Solo permite acceso a usuarios con rol administrador
def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta ruta")
    return current_user


# Decodifica un token sin validar la expiración
def decodeJWT(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
