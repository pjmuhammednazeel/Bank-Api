from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile_phone = Column(String(20))
    balance = Column(Float, nullable=False)
    account_created_on = Column(DateTime, default=datetime.utcnow)
