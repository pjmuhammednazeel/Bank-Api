from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
from database import Base
import enum

class TransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile_phone = Column(String(20))
    balance = Column(Float, nullable=False)
    account_created_on = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # DEPOSIT, WITHDRAW, TRANSFER_IN, TRANSFER_OUT
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(String(200))  # e.g., "Transfer to ACC-0002" or source account
    related_account_id = Column(Integer, nullable=True)  # For transfers, the other account
