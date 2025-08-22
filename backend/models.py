"""
Sol OS MVP Database Models - Security-First ADHD AI Companion
Enhanced with encryption, privacy controls, and GDPR compliance
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """Enhanced user model with security-first design and GDPR compliance"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Security-enhanced email storage
    email_hash = Column(String(255), unique=True, nullable=False, index=True)  # For indexing
    email_encrypted = Column(LargeBinary, nullable=False)  # Actual encrypted email
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt with high rounds
    
    # Account security
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime)
    
    # Privacy and consent management (GDPR compliance)
    data_retention_days = Column(Integer, default=365)
    consent_conversation_storage = Column(Boolean, default=True)
    consent_mood_analysis = Column(Boolean, default=True)
    consent_productivity_optimization = Column(Boolean, default=True)
    consent_analytics_anonymous = Column(Boolean, default=False)
    consent_third_party = Column(Boolean, default=False)
    
    # GDPR data subject rights
    data_export_requested = Column(DateTime)
    data_deletion_requested = Column(DateTime)
    
    # Google Calendar Integration
    google_calendar_access_token = Column(LargeBinary)  # Encrypted OAuth token
    google_calendar_refresh_token = Column(LargeBinary)  # Encrypted refresh token
    google_calendar_token_expires_at = Column(DateTime)
    google_calendar_connected = Column(Boolean, default=False)
    google_calendar_sync_enabled = Column(Boolean, default=True)
    
    # User encryption key management
    encryption_salt = Column(LargeBinary, nullable=False)
    encryption_key_version = Column(String(10), default="v1")
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(45))  # IP address for audit
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    mood_energy_logs = relationship("MoodEnergyLog", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    time_blocks = relationship("TimeBlock", back_populates="user", cascade="all, delete-orphan")
    focus_sessions = relationship("FocusSession", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    """Encrypted conversation storage with minimal complexity for MVP"""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Encrypted conversation content
    message_content_encrypted = Column(LargeBinary, nullable=False)
    sol_response_encrypted = Column(LargeBinary, nullable=False)
    
    # Encryption metadata
    encryption_key_id = Column(String(50), nullable=False)
    
    # Minimal metadata for MVP (no complex memory linking)
    conversation_type = Column(String(20), default='general')
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(String(45))  # IP address for security audit
    
    # Relationships
    user = relationship("User", back_populates="conversations")

class MoodEnergyLog(Base):
    """Simple mood and energy tracking for ADHD patterns"""
    __tablename__ = "mood_energy_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Core tracking data (simple 1-5 scale for MVP)
    mood_rating = Column(Integer, nullable=False)  # 1-5 scale
    energy_level = Column(Integer, nullable=False)  # 1-5 scale
    
    # Optional encrypted notes
    notes_encrypted = Column(LargeBinary)
    encryption_key_id = Column(String(50))
    
    # Simple context (no complex analysis for MVP)
    time_of_day = Column(String(10))  # morning, afternoon, evening
    day_of_week = Column(Integer)
    
    # Input method tracking
    input_method = Column(String(20), default='tap')  # tap, voice, emoji
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="mood_energy_logs")

class Task(Base):
    """Simple ADHD-friendly task management for MVP"""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Basic task details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Simple ADHD features for MVP
    is_broken_down = Column(Boolean, default=False)  # Has been decomposed
    breakdown_steps = Column(JSON, default=[])  # Simple list of micro-tasks
    
    # Basic scheduling
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    
    # Status tracking
    status = Column(String(20), default='pending')  # pending, in_progress, completed
    completion_percentage = Column(Integer, default=0)
    
    # Metadata
    priority = Column(String(10), default='medium')
    category = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="tasks")

class TimeBlock(Base):
    """Simple visual time-blocking for ADHD planning"""
    __tablename__ = "time_blocks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Time block details
    title = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Visual design
    block_type = Column(String(20), default='work')  # work, personal, rest, focus
    color = Column(String(7), default='#4A90E2')  # Hex color for visual organization
    
    # ADHD-specific features
    is_flexible = Column(Boolean, default=False)  # Rigid vs flexible timing
    buffer_time_minutes = Column(Integer, default=10)  # Transition buffer
    
    # Task integration
    linked_task_id = Column(String(36), ForeignKey("tasks.id"))
    
    # Google Calendar sync
    google_calendar_event_id = Column(String(255))  # Google Calendar event ID
    google_calendar_sync_enabled = Column(Boolean, default=True)
    last_synced_at = Column(DateTime)
    sync_status = Column(String(20), default='pending')  # pending, synced, error
    sync_error = Column(Text)  # Store sync error messages
    
    # Additional calendar fields for Google Calendar compatibility
    location = Column(String(500))  # Event location
    description = Column(Text)  # Event description
    all_day = Column(Boolean, default=False)  # All-day event flag
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="time_blocks")
    linked_task = relationship("Task")

class FocusSession(Base):
    """Simple focus timer sessions for MVP"""
    __tablename__ = "focus_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"))
    
    # Session configuration (simple for MVP)
    session_type = Column(String(20), default='pomodoro')  # pomodoro, custom
    planned_duration = Column(Integer, nullable=False)     # Minutes planned
    actual_duration = Column(Integer)                      # Minutes actually focused
    
    # Session tracking
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    completed = Column(Boolean, default=False)
    interruptions = Column(Integer, default=0)
    
    # Simple effectiveness tracking
    focus_rating = Column(Integer)           # 1-5 how focused user felt
    productivity_rating = Column(Integer)    # 1-5 how productive session was
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="focus_sessions")
    task = relationship("Task")

class SecurityAuditLog(Base):
    """Security audit logging for compliance and monitoring"""
    __tablename__ = "security_audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event details
    event_type = Column(String(50), nullable=False)  # login, data_access, consent_change, etc.
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Security context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    success = Column(Boolean, default=True)
    
    # Event details
    event_details = Column(JSON, default={})
    risk_level = Column(String(10), default='low')  # low, medium, high, critical
    
    # Audit trail
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")