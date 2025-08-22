"""
Sol OS MVP - FastAPI Application
ADHD AI Companion with Security-First Architecture
"""

import os
import secrets
import logging
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import SessionLocal, engine
from models import Base, User, Conversation, MoodEnergyLog, Task, TimeBlock, FocusSession
from security import (
    DataEncryptionService, 
    SecureAuthService, 
    SecurityAuditService,
    ConsentManager,
    GDPRComplianceService,
    get_client_ip,
    validate_password_strength
)
from sol_personality import (
    SolPersonalityEngine, 
    ConversationMemoryService,
    ConversationContext
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize services
app = FastAPI(
    title="Sol OS MVP - ADHD AI Companion",
    description="Security-first ADHD productivity companion with Sol's distinctive personality",
    version="1.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security
security = HTTPBearer()
auth_service = SecureAuthService()
encryption_service = DataEncryptionService()
personality_engine = SolPersonalityEngine()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for API
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class MoodEnergyCreate(BaseModel):
    mood_rating: int  # 1-5
    energy_level: int  # 1-5
    notes: Optional[str] = None
    input_method: str = "tap"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    category: Optional[str] = None

class TimeBlockCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    block_type: str = "work"
    color: str = "#4A90E2"
    is_flexible: bool = False

class FocusSessionCreate(BaseModel):
    planned_duration: int  # minutes
    session_type: str = "pomodoro"
    task_id: Optional[str] = None

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Core endpoints
@app.get("/")
async def root():
    return {
        "message": "Sol OS MVP - ADHD AI Companion",
        "version": "1.0.0",
        "personality": "existential, broody, thoughtful, witty",
        "focus": "ADHD productivity support with philosophical depth"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "personality_engine": "active",
            "encryption": "enabled"
        }
    }

# Authentication endpoints
@app.post("/api/v1/auth/register")
@limiter.limit("5/minute")  # Limit registration attempts
async def register_user(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user with security-first approach"""
    
    logger.info("User registration attempt", 
                email_domain=user_data.email.split('@')[1], 
                username=user_data.username,
                ip_address=get_client_ip(request))
    
    # Validate password strength
    if not validate_password_strength(user_data.password):
        logger.warning("Registration failed - weak password", 
                      email_domain=user_data.email.split('@')[1])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    # Check if user already exists
    email_hash = encryption_service.hash_email_for_index(user_data.email)
    existing_user = db.query(User).filter(User.email_hash == email_hash).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check username
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user with encryption
    user_salt = encryption_service.generate_user_salt()
    encrypted_email = encryption_service.encrypt_text(
        user_data.username,  # Use username as temporary user_id for encryption
        user_salt,
        user_data.email
    )
    
    new_user = User(
        email_hash=email_hash,
        email_encrypted=encrypted_email,
        username=user_data.username,
        password_hash=auth_service.hash_password(user_data.password),
        encryption_salt=user_salt,
        created_by=get_client_ip(request)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info("User registration successful", 
                user_id=str(new_user.id),
                username=new_user.username)
    
    # Generate tokens
    access_token = auth_service.create_access_token(str(new_user.id))
    refresh_token = auth_service.create_refresh_token(str(new_user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(new_user.id),
            "username": new_user.username,
            "email": user_data.email
        }
    }

@app.post("/api/v1/auth/login")
@limiter.limit("10/minute")  # Limit login attempts
async def login_user(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user with security measures"""
    
    # Find user
    email_hash = encryption_service.hash_email_for_index(login_data.email)
    user = db.query(User).filter(User.email_hash == email_hash).first()
    
    if not user or not auth_service.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    db.commit()
    
    # Generate tokens
    access_token = auth_service.create_access_token(str(user.id))
    refresh_token = auth_service.create_refresh_token(str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username
        }
    }

# Chat endpoint - Core Sol companion functionality
@app.post("/api/v1/chat")
@limiter.limit("30/minute")  # Reasonable chat limits
async def chat_with_sol(
    request: Request,
    message_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with Sol - Core companion feature"""
    
    # Generate session ID if not provided
    session_id = message_data.session_id or f"session_{secrets.token_urlsafe(8)}"
    
    # Get conversation memory
    memory_service = ConversationMemoryService(db, encryption_service)
    recent_conversations = await memory_service.get_recent_conversations(
        str(current_user.id), session_id, limit=5
    )
    
    # Get user's current mood/energy if available
    latest_mood = db.query(MoodEnergyLog).filter(
        MoodEnergyLog.user_id == current_user.id
    ).order_by(MoodEnergyLog.logged_at.desc()).first()
    
    # Build conversation context
    context = ConversationContext(
        user_id=str(current_user.id),
        session_id=session_id,
        recent_conversations=recent_conversations,
        user_mood=latest_mood.mood_rating if latest_mood else None,
        user_energy=latest_mood.energy_level if latest_mood else None,
        time_of_day=datetime.now().strftime("%H")
    )
    
    # Generate Sol's response
    sol_response = await personality_engine.generate_response(message_data.message, context)
    
    # Store conversation
    conversation_id = await memory_service.store_conversation(
        str(current_user.id),
        session_id,
        message_data.message,
        sol_response.response_text,
        sol_response.conversation_type
    )
    
    return {
        "response": sol_response.response_text,
        "session_id": session_id,
        "conversation_id": conversation_id,
        "conversation_type": sol_response.conversation_type,
        "response_time_ms": sol_response.response_time_ms,
        "personality_indicators": sol_response.personality_indicators
    }

# Mood/Energy logging endpoint
@app.post("/api/v1/mood-energy")
async def log_mood_energy(
    mood_data: MoodEnergyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick mood and energy logging for ADHD pattern tracking"""
    
    # Validate input ranges
    if not (1 <= mood_data.mood_rating <= 5) or not (1 <= mood_data.energy_level <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mood and energy ratings must be between 1 and 5"
        )
    
    # Determine time of day
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        time_of_day = "morning"
    elif 12 <= current_hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"
    
    # Encrypt notes if provided
    notes_encrypted = None
    encryption_key_id = None
    if mood_data.notes:
        notes_encrypted = encryption_service.encrypt_text(
            str(current_user.id), current_user.encryption_salt, mood_data.notes
        )
        encryption_key_id = f"user:{current_user.id}:v1"
    
    # Create mood log
    mood_log = MoodEnergyLog(
        user_id=current_user.id,
        mood_rating=mood_data.mood_rating,
        energy_level=mood_data.energy_level,
        notes_encrypted=notes_encrypted,
        encryption_key_id=encryption_key_id,
        time_of_day=time_of_day,
        day_of_week=datetime.now().weekday(),
        input_method=mood_data.input_method
    )
    
    db.add(mood_log)
    db.commit()
    
    return {
        "id": str(mood_log.id),
        "mood_rating": mood_log.mood_rating,
        "energy_level": mood_log.energy_level,
        "time_of_day": mood_log.time_of_day,
        "logged_at": mood_log.logged_at.isoformat()
    }

# Task management endpoints
@app.post("/api/v1/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new task with ADHD-friendly features"""
    
    task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        category=task_data.category
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": task.created_at.isoformat()
    }

@app.get("/api/v1/tasks")
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's tasks"""
    
    tasks = db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.created_at.desc()).all()
    
    return [
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "is_broken_down": task.is_broken_down,
            "breakdown_steps": task.breakdown_steps,
            "created_at": task.created_at.isoformat()
        }
        for task in tasks
    ]

@app.get("/api/v1/sol/personality")
async def get_sol_personality():
    """Get Sol's personality summary for users"""
    return personality_engine.get_personality_summary()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)