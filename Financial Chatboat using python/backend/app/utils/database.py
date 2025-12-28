from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import logging
from typing import AsyncGenerator

from app.config import settings

logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    user_message = Column(Text)
    bot_response = Column(Text)
    sentiment_label = Column(String)
    sentiment_confidence = Column(Float)
    response_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FineTuningTask(Base):
    __tablename__ = "fine_tuning_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    dataset_name = Column(String)
    status = Column(String)  # queued, running, completed, failed, cancelled
    progress = Column(Float, default=0.0)
    model_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    parameters = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)
    version = Column(String)
    model_path = Column(String)
    is_active = Column(Boolean, default=False)
    performance_metrics = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String)
    message_id = Column(String)
    rating = Column(Integer)  # 1-5 star rating
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

async def init_db():
    """Initialize database tables"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_db() -> AsyncGenerator[Session, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database utility functions
def save_chat_session(
    db: Session,
    conversation_id: str,
    user_message: str,
    bot_response: str,
    sentiment_label: str,
    sentiment_confidence: float,
    response_time: float
):
    """Save chat session to database"""
    try:
        chat_session = ChatSession(
            conversation_id=conversation_id,
            user_message=user_message,
            bot_response=bot_response,
            sentiment_label=sentiment_label,
            sentiment_confidence=sentiment_confidence,
            response_time=response_time
        )
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        return chat_session
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving chat session: {e}")
        raise

def get_chat_history(db: Session, conversation_id: str, limit: int = 50):
    """Get chat history for a conversation"""
    try:
        return db.query(ChatSession).filter(
            ChatSession.conversation_id == conversation_id
        ).order_by(ChatSession.created_at.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise

def save_fine_tuning_task(
    db: Session,
    task_id: str,
    dataset_name: str,
    parameters: dict
):
    """Save fine-tuning task to database"""
    try:
        import json
        task = FineTuningTask(
            task_id=task_id,
            dataset_name=dataset_name,
            status="queued",
            parameters=json.dumps(parameters)
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving fine-tuning task: {e}")
        raise

def update_fine_tuning_task(
    db: Session,
    task_id: str,
    **kwargs
):
    """Update fine-tuning task status"""
    try:
        task = db.query(FineTuningTask).filter(
            FineTuningTask.task_id == task_id
        ).first()
        
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            db.commit()
            db.refresh(task)
            return task
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating fine-tuning task: {e}")
        raise

def get_fine_tuning_task(db: Session, task_id: str):
    """Get fine-tuning task by ID"""
    try:
        return db.query(FineTuningTask).filter(
            FineTuningTask.task_id == task_id
        ).first()
    except Exception as e:
        logger.error(f"Error getting fine-tuning task: {e}")
        raise
