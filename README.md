# Bank API (PostgreSQL)

This backend uses PostgreSQL via SQLAlchemy.

## Setup

1. Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

2. Set the `DATABASE_URL` environment variable (PowerShell):

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:<YOUR_PASSWORD>@localhost:5432/bank_api"
```

Create the `bank_api` database with your Postgres client if it doesn't exist.

3. Run the API:

```powershell
uvicorn backend.main:app --reload
```

## Notes
- The field `address` was replaced with `mobile_phone` across models and schemas.
- Tables are created on startup via `models.Base.metadata.create_all(bind=engine)`.
