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

## Frontend (HTML/CSS/JS)
- Files are in `frontend/` (no framework required).
- Ensure the API is running on `http://localhost:8000`.

Open the page in a simple static server (recommended):

```powershell
# From repo root
python -m http.server 5500 -d frontend
# Then open http://localhost:5500
```

Or open `frontend/index.html` directly in the browser; CORS is enabled.

The UI allows you to:
- Create an account (account number, name, mobile phone, balance)
- List accounts
