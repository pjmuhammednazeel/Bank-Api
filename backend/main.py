from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bank Account API")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Register Account
# -------------------------
@app.post("/register", response_model=schemas.AccountResponse)
def register_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    
    existing = db.query(models.Account).filter(
        models.Account.account_number == account.account_number
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Account number already exists")

    new_account = models.Account(
        account_number=account.account_number,
        name=account.name,
        mobile_phone=account.mobile_phone,
        balance=account.balance
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account

# -------------------------
# Get All Accounts
# -------------------------
@app.get("/accounts", response_model=list[schemas.AccountResponse])
def get_accounts(db: Session = Depends(get_db)):
    return db.query(models.Account).all()

# -------------------------
# Get Account by ID
# -------------------------
@app.get("/accounts/{account_id}", response_model=schemas.AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account
