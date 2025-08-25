from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class Report(Base):
    """Oracle BI Publisher Report model"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    oracle_report_path = Column(String(500))
    ai_generated_query = Column(Text)
    parameters = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))


class AIInteraction(Base):
    """AI interaction tracking model"""
    __tablename__ = "ai_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text)
    sql_generated = Column(Text)
    report_id = Column(Integer)
    session_id = Column(String(100))
    processing_time = Column(Integer)  # milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_successful = Column(Boolean, default=True)


class UserSession(Base):
    """User session tracking model"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100))
    oracle_username = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)