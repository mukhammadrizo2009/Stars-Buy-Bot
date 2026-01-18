from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    DateTime,
    )
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    
    name = Column(String(length=25))
    phone_number = Column(String(length=13))
    balance = Column(BigInteger, default=0,)
    stars = Column(BigInteger, default=0)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    

class StarPackage(Base):
    __tablename__ = "star_packages"

    id = Column(Integer, primary_key=True)
    stars = Column(Integer, nullable=False, unique=True)
    price = Column(BigInteger, nullable=False)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
