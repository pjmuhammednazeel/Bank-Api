from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AccountCreate(BaseModel):
    account_number: str
    name: str
    mobile_phone: str
    balance: float

class AccountResponse(AccountCreate):
    id: int
    account_created_on: datetime

    class Config:
        orm_mode = True

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    transaction_type: str
    amount: float
    balance_before: float
    balance_after: float
    timestamp: datetime
    description: Optional[str]
    related_account_id: Optional[int]

    class Config:
        orm_mode = True

class DepositRequest(BaseModel):
    account_number: str
    amount: float = Field(gt=0, description="Deposit amount must be positive")

class WithdrawRequest(BaseModel):
    account_number: str
    amount: float = Field(gt=0, description="Withdraw amount must be positive")

class TransferRequest(BaseModel):
    from_account_number: str
    to_account_number: str
    amount: float = Field(gt=0, description="Transfer amount must be positive")
