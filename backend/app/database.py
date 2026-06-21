"""
Database configuration and SQLAlchemy models for the DevSecOps Diary API.
"""
import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dagbok.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DiaryEntryModel(Base):
    """
    SQLAlchemy ORM model representing a diary entry in the database.
    """
    # pylint: disable=too-few-public-methods
    __tablename__ = "diary_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime,
                        default=lambda: datetime.datetime.now(
                            datetime.timezone.utc).replace(tzinfo=None)
                        )

def get_db():
    """
    Dependency function to generate and yield a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
