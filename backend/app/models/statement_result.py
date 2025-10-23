"""Statement Result Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StatementResult(Base):
    """Model for storing parsed statement results"""
    __tablename__ = "statement_results"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String, index=True, nullable=True)
    card_issuer = Column(String, nullable=True)
    statement_date = Column(String, nullable=True)
    due_date = Column(String, nullable=True)
    total_amount_due = Column(String, nullable=True)
    overall_confidence = Column(Float, nullable=True)
    parser_used = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<StatementResult(id={self.id}, card_issuer={self.card_issuer})>"