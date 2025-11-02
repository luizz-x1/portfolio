from datetime import datetime
from sqlalchemy.orm import Session
from models.models import Meeting

def create_meeting(
    db: Session,
    chat_id: int,
    organizer_id: int,
    title: str,
    description: str = None,
    meeting_link: str = None,
    scheduled_at: datetime = None,
    status: str = "pending",
):
    """Crea una nueva reunión en la base de datos."""
    db_meeting = Meeting(
        chat_id=chat_id,
        organizer_id=organizer_id,
        title=title,
        description=description,
        meeting_link=meeting_link,
        scheduled_at=scheduled_at or datetime.now(),
        status=status,
        created_at=datetime.now()
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting
