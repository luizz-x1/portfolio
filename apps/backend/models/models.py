from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# --------------------
# USERS
# --------------------
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    role = Column(String(50), default="visitor") 
    create_at = Column(DateTime, nullable=False)
    last_connection = Column(DateTime, nullable=True)

    # Relaciones
    messages = relationship("Message", back_populates="sender")
    chat_participants = relationship("ChatParticipant", back_populates="user")
    organized_meetings = relationship("Meeting", back_populates="organizer")
    meeting_participations = relationship("MeetingParticipant", back_populates="user")


# --------------------
# CHATS
# --------------------
class Chat(Base):
    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    is_group = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)

    # Relaciones
    messages = relationship("Message", back_populates="chat")
    participants = relationship("ChatParticipant", back_populates="chat")
    meetings = relationship("Meeting", back_populates="chat")


# --------------------
# CHAT PARTICIPANTS
# --------------------
class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, nullable=False)

    # Relaciones
    chat = relationship("Chat", back_populates="participants")
    user = relationship("User", back_populates="chat_participants")


# --------------------
# MESSAGES
# --------------------
class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relaciones
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")


# --------------------
# MEETINGS
# --------------------
class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), nullable=False)
    organizer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    meeting_link = Column(String(500), nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)  # pending, accepted, cancelled
    created_at = Column(DateTime, nullable=False)

    # Relaciones
    chat = relationship("Chat", back_populates="meetings")
    organizer = relationship("User", back_populates="organized_meetings")
    participants = relationship("MeetingParticipant", back_populates="meeting")


# --------------------
# MEETING PARTICIPANTS
# --------------------
class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    meeting_id = Column(BigInteger, ForeignKey("meetings.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    response = Column(String(50), nullable=True)  # accepted, rejected, pending
    responded_at = Column(DateTime, nullable=True)

    # Relaciones
    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="meeting_participations")
