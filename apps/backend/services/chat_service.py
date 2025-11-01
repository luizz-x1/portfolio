from crud import crud_chats, crud_messages
from services.ws_service import send_message_to_user
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Crear o recuperar un chat entre dos usuarios
def create_or_get_chat(db: Session, sender_id: int, receiver_id: int):
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="No puedes crear un chat contigo mismo")

    chat = crud_chats.get_private_chat_between_users(db, sender_id, receiver_id)
    return chat or crud_chats.create_private_chat(db, sender_id, receiver_id)


# Obtener todos los chats del usuario
def get_user_chats(db: Session, user_id: int):
    return crud_chats.get_user_chats(db, user_id)


# Crear y enviar mensaje
async def create_and_send_message(db: Session, message, sender_id: int):
    new_message = crud_messages.create_message(db, message)
    participants = crud_chats.get_chat_participants(db, message.chat_id)

    message_data = {
        "type": "message",
        "message_id": new_message.id,
        "chat_id": message.chat_id,
        "from": sender_id,
        "content": message.content,
    }

    for user_id in participants:
        if user_id != sender_id:
            delivered = await send_message_to_user(user_id, message_data)
            if delivered:
                await crud_messages.update_status(db, new_message.id, "delivered")

    return new_message


# Obtener mensajes del chat
def get_chat_messages(db: Session, chat_id: int, skip=0, limit=100):
    return crud_messages.get_chat_messages(db, chat_id, skip, limit)


# Obtener contactos con los que el usuario tiene chats
def get_contacts_for_notifications(db: Session, user_id: int):
    return crud_chats.get_contacts_for_user(db, user_id)
