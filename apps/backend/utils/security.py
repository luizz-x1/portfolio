from jose import JWTError, jwt
from datetime import datetime, timedelta

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