from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON
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
    

class PaymentCard(Base):
    __tablename__ = "payment_cards"

    id = Column(Integer, primary_key=True)
    card_number = Column(String(32), nullable=False)
    card_type = Column(String(20))
    is_active = Column(Boolean, default=True)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    amount = Column(Integer)
    status = Column(String, default="pending")
    admin_messages = Column(JSON)

class StarsOrder(Base):
    __tablename__ = "stars_orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger) 
    stars = Column(BigInteger)
    price = Column(BigInteger)
    status = Column(String, default="pending")
    admin_messages = Column(JSON)