from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create the session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the base class for all models
class Base(DeclarativeBase):
    pass

# Get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()