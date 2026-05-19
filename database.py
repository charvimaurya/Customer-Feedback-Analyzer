import os
import time
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/customer_feedback")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Feedback(Base):
    """
    Unified table for storing customer feedback at all stages.
    - Raw responses: stored in raw_content
    - Processed responses: stored in processed_content
    - Positive/Negative responses: reflected in the sentiment column
    """
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_content = Column(Text, nullable=False)
    processed_content = Column(Text, nullable=True)
    sentiment = Column(String(20), index=True) # e.g., 'Good', 'Bad', 'Neutral'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # V1 PIS fields
    intensity_score = Column(Integer, nullable=True) # 1-10
    revenue_risk_flag = Column(Boolean, default=False)
    insight_category = Column(String(255), index=True, nullable=True)

    def __repr__(self):
        return f"<Feedback(id={self.id}, sentiment='{self.sentiment}', category='{self.insight_category}')>"

class InsightScore(Base):
    """
    Table for caching aggregated Problem Impact Scores (PIS) for insights.
    """
    __tablename__ = "insight_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(255), unique=True, index=True)
    total_reviews = Column(Integer, default=0)
    pis_score = Column(Float, default=0.0)
    last_calculated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InsightScore(category='{self.category}', pis_score={self.pis_score})>"

def init_db():
    retries = 5
    while retries > 0:
        try:
            # Note: In a production app, we'd use Alembic for migrations.
            # To avoid issues with table schemas changing, we'll try to create them.
            Base.metadata.create_all(bind=engine)
            print("Database initialized successfully with unified Feedback table.")
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
