from pydantic import BaseModel
from datetime import datetime

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
