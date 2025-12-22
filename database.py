import os
import time
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/customer_feedback")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 1. Table for Raw Data Storage
class RawFeedback(Base):
    __tablename__ = "raw_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    review = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 2. Table for Cleaned Data Storage
class CleanedFeedback(Base):
    __tablename__ = "cleaned_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    cleaned_review = Column(String, nullable=False)
    source_id = Column(Integer) # Link to raw data
    created_at = Column(DateTime, default=datetime.utcnow)

# 3. Table for Positive Responses
class PositiveFeedback(Base):
    __tablename__ = "positive_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    review = Column(String, nullable=False)
    sentiment = Column(String, default="Good")
    created_at = Column(DateTime, default=datetime.utcnow)

# 4. Table for Negative Responses
class NegativeFeedback(Base):
    __tablename__ = "negative_feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    review = Column(String, nullable=False)
    sentiment = Column(String, default="Bad")
    created_at = Column(DateTime, default=datetime.utcnow)

# Fallback/Legacy table (optional, keeping it for compatibility if needed, but let's stick to the 4 requested)
class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    review = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("Database initialized successfully with 4 main tables.")
            return
        except Exception as e:
            print(f"Database not ready, retrying... ({retries} left). Error: {e}")
            retries -= 1
            time.sleep(5)
    print("Could not connect to the database after multiple retries.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
