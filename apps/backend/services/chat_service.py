from sqlalchemy.orm import Session
from config.database import get_db
from crud.crud_chats import get_user_chats, get_chat_participants

async def get_contacts_for_notifications(user_id: int):
    """
    Retorna los IDs de los contactos con los que el usuario
    ha tenido alguna conversación.
    """
    db_gen = get_db()
    db: Session = next(db_gen)

    try:
        chats = get_user_chats(db, user_id)
        contact_ids = set()

        for chat in chats:
            participants = get_chat_participants(db, chat.id)
            for pid in participants:
                if pid != user_id:
                    contact_ids.add(pid)

        return list(contact_ids)

    finally:
        db.close()
        db_gen.close()