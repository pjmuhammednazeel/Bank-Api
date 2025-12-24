from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bank Account API")

# CORS for local HTML/JS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

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

# -------------------------
# Delete Account
# -------------------------
@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()

    return {"message": f"Account {account_id} deleted successfully"}

# -------------------------
# Deposit
# -------------------------
@app.post("/accounts/deposit")
def deposit(req: schemas.DepositRequest, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_number == req.account_number).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    balance_before = account.balance
    account.balance += req.amount
    
    transaction = models.Transaction(
        account_id=account.id,
        transaction_type="DEPOSIT",
        amount=req.amount,
        balance_before=balance_before,
        balance_after=account.balance,
        description="Deposit"
    )
    
    db.add(account)
    db.add(transaction)
    db.commit()
    db.refresh(account)
    
    return {"account": account, "transaction": transaction}

# -------------------------
# Withdraw
# -------------------------
@app.post("/accounts/withdraw")
def withdraw(req: schemas.WithdrawRequest, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_number == req.account_number).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if account.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    balance_before = account.balance
    account.balance -= req.amount
    
    transaction = models.Transaction(
        account_id=account.id,
        transaction_type="WITHDRAW",
        amount=req.amount,
        balance_before=balance_before,
        balance_after=account.balance,
        description="Withdrawal"
    )
    
    db.add(account)
    db.add(transaction)
    db.commit()
    db.refresh(account)
    
    return {"account": account, "transaction": transaction}

# -------------------------
# Transfer
# -------------------------
@app.post("/accounts/transfer")
def transfer(req: schemas.TransferRequest, db: Session = Depends(get_db)):
    if req.from_account_number == req.to_account_number:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    from_account = db.query(models.Account).filter(models.Account.account_number == req.from_account_number).first()
    to_account = db.query(models.Account).filter(models.Account.account_number == req.to_account_number).first()
    
    if not from_account:
        raise HTTPException(status_code=404, detail="Sender account not found")
    if not to_account:
        raise HTTPException(status_code=404, detail="Recipient account not found")
    
    if from_account.balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    from_balance_before = from_account.balance
    from_account.balance -= req.amount
    
    from_txn = models.Transaction(
        account_id=from_account.id,
        transaction_type="TRANSFER_OUT",
        amount=req.amount,
        balance_before=from_balance_before,
        balance_after=from_account.balance,
        description=f"Transfer to {to_account.account_number}",
        related_account_id=to_account.id
    )
    
    to_balance_before = to_account.balance
    to_account.balance += req.amount
    
    to_txn = models.Transaction(
        account_id=to_account.id,
        transaction_type="TRANSFER_IN",
        amount=req.amount,
        balance_before=to_balance_before,
        balance_after=to_account.balance,
        description=f"Transfer from {from_account.account_number}",
        related_account_id=from_account.id
    )
    
    db.add(from_account)
    db.add(to_account)
    db.add(from_txn)
    db.add(to_txn)
    db.commit()
    
    return {
        "from_account": from_account,
        "to_account": to_account,
        "from_transaction": from_txn,
        "to_transaction": to_txn
    }

# -------------------------
# Transaction History
# -------------------------
@app.get("/accounts/{account_number}/transactions", response_model=list[schemas.TransactionResponse])
def get_transactions(account_number: str, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transactions = db.query(models.Transaction).filter(
        models.Transaction.account_id == account.id
    ).order_by(models.Transaction.timestamp.desc()).all()
    
    return transactions


# -------------------------
# Verify & Fix Balance
# -------------------------
@app.post("/accounts/{account_id}/verify-balance")
def verify_balance(account_id: int, db: Session = Depends(get_db)):
    """Recalculates account balance based on latest transaction and fixes if inconsistent"""
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get the latest transaction for this account
    latest_txn = db.query(models.Transaction).filter(
        models.Transaction.account_id == account_id
    ).order_by(models.Transaction.timestamp.desc()).first()
    
    if not latest_txn:
        # No transactions, balance should be 0 or initial
        return {"status": "ok", "account_id": account.id, "message": "No transactions found", "current_balance": account.balance}
    
    # Fix balance to match latest transaction's after balance
    correct_balance = latest_txn.balance_after
    old_balance = account.balance
    account.balance = correct_balance
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return {
        "status": "fixed",
        "account_id": account.id,
        "old_balance": old_balance,
        "correct_balance": correct_balance,
        "message": "Balance has been corrected based on transaction history"
    }
