import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from sqlalchemy.orm import Session

from models.models import User, Base

from config.database import SessionLocal, engine


def create_admin_user():

    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
    
        existing_admin = session.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print("✅ Usuario admin ya existe")
            return existing_admin
        
    
        admin_user = User(
            unique_id="admin_main",
            email="ls7010425@gmail.com",
            name="Luis", 
            role="admin",
            create_at=datetime.now(),
            last_connection=datetime.now()
        )
        
        session.add(admin_user)
        session.commit()
        print("✅ Usuario admin creado exitosamente")
        return admin_user
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creando admin: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_admin_user()