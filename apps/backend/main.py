from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import engine
from models.models import Base
from api.endpoints import users, auth, chat, status
from api.websocket import ws
from utils.redis import init_redis

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio Chat API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos
@app.on_event("startup")
async def startup():
    await init_redis()

# @app.on_event("shutdown")
# async def shutdown():
#     await close_redis()

# Routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(ws.router, tags=["websocket"])