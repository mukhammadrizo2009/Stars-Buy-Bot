from .database import LocalSession
from .models import User

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def get_all_users():
    with LocalSession() as session:
        users = session.query(User).all()
        return users
