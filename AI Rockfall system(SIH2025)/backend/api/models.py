"""
Database models and connection setup for AI Rockfall Prediction System
======================================================================

SQLAlchemy models for PostgreSQL database with proper relationships and constraints.

Models:
- User: System users with authentication
- Site: Mining sites with location and configuration
- Device: Sensor devices with specifications
- Analysis: Analysis runs with results and metadata
- Alert: System alerts and notifications

Author: AI Rockfall Prediction Team
Date: October 26, 2025
"""

from datetime import datetime
from typing import Generator
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, Text,
    ForeignKey, JSON, Enum, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import enum

from .config import settings

Base = declarative_base()

class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class AnalysisStatus(enum.Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AlertSeverity(enum.Enum):
    """Alert severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DeviceType(enum.Enum):
    """Device type enumeration."""
    LIDAR = "lidar"
    GEOPHONE = "geophone"
    PIEZOMETER = "piezometer"
    GBINSAR = "gbinsar"
    EXTENSOMETER = "extensometer"
    WEATHER_STATION = "weather_station"
    CAMERA = "camera"

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sites = relationship("Site", back_populates="created_by")
    analyses = relationship("Analysis", back_populates="created_by")
    alerts = relationship("Alert", back_populates="created_by")

class Site(Base):
    """Mining site model with location and configuration."""
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float)
    area_sqkm = Column(Float)
    mining_type = Column(String(50))  # open-pit, underground, etc.
    status = Column(String(20), default="active")  # active, inactive, maintenance
    configuration = Column(JSON)  # Site-specific configuration
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="sites")
    devices = relationship("Device", back_populates="site", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="site", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="site", cascade="all, delete-orphan")

class Device(Base):
    """Sensor device model with specifications and status."""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    location_lat = Column(Float)
    location_lng = Column(Float)
    location_description = Column(Text)
    installation_date = Column(DateTime)
    last_calibration = Column(DateTime)
    status = Column(String(20), default="active")  # active, inactive, maintenance, offline
    specifications = Column(JSON)  # Device-specific specs
    configuration = Column(JSON)  # Device configuration
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    site = relationship("Site", back_populates="devices")
    analyses = relationship("Analysis", back_populates="device", cascade="all, delete-orphan")

class Analysis(Base):
    """Analysis run model with results and metadata."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))
    analysis_type = Column(String(50), nullable=False)  # lidar, geophone, etc.
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    parameters = Column(JSON)  # Analysis parameters
    results = Column(JSON)  # Analysis results
    risk_score = Column(Float)
    risk_level = Column(String(20))  # low, medium, high, critical
    execution_time_seconds = Column(Float)
    error_message = Column(Text)
    input_files = Column(JSON)  # List of input file paths
    output_files = Column(JSON)  # List of output file paths
    created_by_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    site = relationship("Site", back_populates="analyses")
    device = relationship("Device", back_populates="analyses")
    created_by = relationship("User", back_populates="analyses")
    alerts = relationship("Alert", back_populates="analysis", cascade="all, delete-orphan")

class Alert(Base):
    """System alert model for notifications."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM, nullable=False)
    alert_type = Column(String(50), nullable=False)  # risk, system, maintenance, etc.
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by_id = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    metadata = Column(JSON)  # Additional alert data
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    site = relationship("Site", back_populates="alerts")
    analysis = relationship("Analysis", back_populates="alerts")
    created_by = relationship("User", back_populates="alerts")
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_id])

# Database engine and session
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all database tables (for testing/reset)."""
    Base.metadata.drop_all(bind=engine)