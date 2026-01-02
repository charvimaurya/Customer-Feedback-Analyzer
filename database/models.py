from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database.db import Base

# 1. Raw feedback
class RawFeedback(Base):
    __tablename__ = "raw_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    review = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# 2. Cleaned feedback
class CleanedFeedback(Base):
    __tablename__ = "cleaned_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    cleaned_review = Column(Text, nullable=False)
    source_id = Column(Integer)  # references RawFeedback.id
    created_at = Column(DateTime, server_default=func.now())


# 3. Positive feedback
class PositiveFeedback(Base):
    __tablename__ = "positive_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    review = Column(Text, nullable=False)
    sentiment = Column(String(10), default="Good")
    created_at = Column(DateTime, server_default=func.now())


# 4. Negative feedback
class NegativeFeedback(Base):
    __tablename__ = "negative_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    review = Column(Text, nullable=False)
    sentiment = Column(String(10), default="Bad")
    created_at = Column(DateTime, server_default=func.now())


# 5. Legacy unified table
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    review = Column(Text, nullable=False)
    sentiment = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
