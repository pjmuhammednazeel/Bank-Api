from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# CHANGE these values according to your PostgreSQL setup
DATABASE_URL = "postgresql+psycopg2://bank_user:123@localhost:5432/bank_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
