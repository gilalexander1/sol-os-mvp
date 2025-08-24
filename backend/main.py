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
from models import Base, User, Conversation, MoodEnergyLog, Task, TimeBlock, FocusSession, JournalEntry
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
from routers import calendar

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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    body = await request.body()
    logger.info(f"Incoming {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    if body:
        logger.info(f"Request body: {body}")
    
    # Restore body for the next handler
    async def receive():
        return {"type": "http.request", "body": body}
    
    request._receive = receive
    
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

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

# Include routers
app.include_router(calendar.router)

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

class JournalEntryCreate(BaseModel):
    title: str
    content: str
    mood_rating: Optional[int] = None       # 1-10
    energy_level: Optional[int] = None      # 1-10
    focus_level: Optional[int] = None       # 1-10
    anxiety_level: Optional[int] = None     # 1-10
    accomplishments: Optional[str] = None
    challenges: Optional[str] = None
    gratitude: Optional[str] = None
    tomorrow_focus: Optional[str] = None
    emotional_tags: Optional[List[str]] = []
    entry_date: Optional[datetime] = None   # Defaults to today
    is_favorite: bool = False

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood_rating: Optional[int] = None
    energy_level: Optional[int] = None
    focus_level: Optional[int] = None
    anxiety_level: Optional[int] = None
    accomplishments: Optional[str] = None
    challenges: Optional[str] = None
    gratitude: Optional[str] = None
    tomorrow_focus: Optional[str] = None
    emotional_tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

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
    
    # Debug logging for frontend requests
    client_ip = get_client_ip(request)
    logger.info(f"Login attempt from {client_ip} - Email: {login_data.email}")
    
    # Find user
    email_hash = encryption_service.hash_email_for_index(login_data.email)
    user = db.query(User).filter(User.email_hash == email_hash).first()
    
    if not user:
        logger.warning(f"User not found for email: {login_data.email}")
    else:
        logger.info(f"User found: {user.username}, checking password...")
    
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

@app.patch("/api/v1/tasks/{task_id}")
async def update_task(
    task_id: str,
    task_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task"""
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update allowed fields
    if "status" in task_data:
        task.status = task_data["status"]
    if "scheduled_start" in task_data:
        task.scheduled_start = task_data["scheduled_start"] if task_data["scheduled_start"] else None
    if "scheduled_end" in task_data:
        task.scheduled_end = task_data["scheduled_end"] if task_data["scheduled_end"] else None
    if "title" in task_data:
        task.title = task_data["title"]
    if "description" in task_data:
        task.description = task_data["description"]
    if "priority" in task_data:
        task.priority = task_data["priority"]
    
    task.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "scheduled_start": task.scheduled_start.isoformat() if task.scheduled_start else None,
        "scheduled_end": task.scheduled_end.isoformat() if task.scheduled_end else None,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete task"""
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

# Journal management endpoints
@app.post("/api/v1/journal")
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new journal entry"""
    
    # Set entry date to today if not provided
    entry_date = entry_data.entry_date or datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Encrypt sensitive content
    encrypted_title = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.title)
    encrypted_content = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.content)
    
    encrypted_accomplishments = None
    encrypted_challenges = None
    encrypted_gratitude = None
    encrypted_tomorrow_focus = None
    
    if entry_data.accomplishments:
        encrypted_accomplishments = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.accomplishments)
    if entry_data.challenges:
        encrypted_challenges = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.challenges)
    if entry_data.gratitude:
        encrypted_gratitude = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.gratitude)
    if entry_data.tomorrow_focus:
        encrypted_tomorrow_focus = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.tomorrow_focus)
    
    # Create journal entry
    journal_entry = JournalEntry(
        user_id=current_user.id,
        title=encrypted_title,
        content=encrypted_content,
        mood_rating=entry_data.mood_rating,
        energy_level=entry_data.energy_level,
        focus_level=entry_data.focus_level,
        anxiety_level=entry_data.anxiety_level,
        accomplishments=encrypted_accomplishments,
        challenges=encrypted_challenges,
        gratitude=encrypted_gratitude,
        tomorrow_focus=encrypted_tomorrow_focus,
        emotional_tags=entry_data.emotional_tags,
        entry_date=entry_date,
        is_favorite=entry_data.is_favorite
    )
    
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    
    # Return decrypted entry
    return {
        "id": str(journal_entry.id),
        "title": entry_data.title,
        "content": entry_data.content,
        "mood_rating": journal_entry.mood_rating,
        "energy_level": journal_entry.energy_level,
        "focus_level": journal_entry.focus_level,
        "anxiety_level": journal_entry.anxiety_level,
        "accomplishments": entry_data.accomplishments,
        "challenges": entry_data.challenges,
        "gratitude": entry_data.gratitude,
        "tomorrow_focus": entry_data.tomorrow_focus,
        "emotional_tags": journal_entry.emotional_tags,
        "entry_date": journal_entry.entry_date.isoformat(),
        "is_favorite": journal_entry.is_favorite,
        "created_at": journal_entry.created_at.isoformat(),
        "updated_at": journal_entry.updated_at.isoformat()
    }

@app.get("/api/v1/journal")
async def get_journal_entries(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's journal entries"""
    
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id
    ).order_by(JournalEntry.entry_date.desc()).offset(offset).limit(limit).all()
    
    # Decrypt and return entries
    decrypted_entries = []
    for entry in entries:
        decrypted_entries.append({
            "id": str(entry.id),
            "title": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.title),
            "content": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.content),
            "mood_rating": entry.mood_rating,
            "energy_level": entry.energy_level,
            "focus_level": entry.focus_level,
            "anxiety_level": entry.anxiety_level,
            "accomplishments": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.accomplishments) if entry.accomplishments else None,
            "challenges": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.challenges) if entry.challenges else None,
            "gratitude": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.gratitude) if entry.gratitude else None,
            "tomorrow_focus": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.tomorrow_focus) if entry.tomorrow_focus else None,
            "emotional_tags": entry.emotional_tags,
            "entry_date": entry.entry_date.isoformat(),
            "is_favorite": entry.is_favorite,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat()
        })
    
    return {"entries": decrypted_entries}

@app.get("/api/v1/journal/{entry_id}")
async def get_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific journal entry"""
    
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    return {
        "id": str(entry.id),
        "title": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.title),
        "content": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.content),
        "mood_rating": entry.mood_rating,
        "energy_level": entry.energy_level,
        "focus_level": entry.focus_level,
        "anxiety_level": entry.anxiety_level,
        "accomplishments": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.accomplishments) if entry.accomplishments else None,
        "challenges": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.challenges) if entry.challenges else None,
        "gratitude": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.gratitude) if entry.gratitude else None,
        "tomorrow_focus": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.tomorrow_focus) if entry.tomorrow_focus else None,
        "emotional_tags": entry.emotional_tags,
        "entry_date": entry.entry_date.isoformat(),
        "is_favorite": entry.is_favorite,
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat()
    }

@app.patch("/api/v1/journal/{entry_id}")
async def update_journal_entry(
    entry_id: str,
    entry_data: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a journal entry"""
    
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    # Update fields that were provided
    if entry_data.title is not None:
        entry.title = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.title)
    if entry_data.content is not None:
        entry.content = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.content)
    if entry_data.mood_rating is not None:
        entry.mood_rating = entry_data.mood_rating
    if entry_data.energy_level is not None:
        entry.energy_level = entry_data.energy_level
    if entry_data.focus_level is not None:
        entry.focus_level = entry_data.focus_level
    if entry_data.anxiety_level is not None:
        entry.anxiety_level = entry_data.anxiety_level
    if entry_data.accomplishments is not None:
        entry.accomplishments = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.accomplishments) if entry_data.accomplishments else None
    if entry_data.challenges is not None:
        entry.challenges = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.challenges) if entry_data.challenges else None
    if entry_data.gratitude is not None:
        entry.gratitude = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.gratitude) if entry_data.gratitude else None
    if entry_data.tomorrow_focus is not None:
        entry.tomorrow_focus = encryption_service.encrypt_text(current_user.id, current_user.encryption_salt, entry_data.tomorrow_focus) if entry_data.tomorrow_focus else None
    if entry_data.emotional_tags is not None:
        entry.emotional_tags = entry_data.emotional_tags
    if entry_data.is_favorite is not None:
        entry.is_favorite = entry_data.is_favorite
    
    entry.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": str(entry.id),
        "title": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.title),
        "content": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.content),
        "mood_rating": entry.mood_rating,
        "energy_level": entry.energy_level,
        "focus_level": entry.focus_level,
        "anxiety_level": entry.anxiety_level,
        "accomplishments": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.accomplishments) if entry.accomplishments else None,
        "challenges": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.challenges) if entry.challenges else None,
        "gratitude": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.gratitude) if entry.gratitude else None,
        "tomorrow_focus": encryption_service.decrypt_text(current_user.id, current_user.encryption_salt, entry.tomorrow_focus) if entry.tomorrow_focus else None,
        "emotional_tags": entry.emotional_tags,
        "entry_date": entry.entry_date.isoformat(),
        "is_favorite": entry.is_favorite,
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat()
    }

@app.delete("/api/v1/journal/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a journal entry"""
    
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Journal entry deleted successfully"}

@app.get("/api/v1/sol/personality")
async def get_sol_personality():
    """Get Sol's personality summary for users"""
    return personality_engine.get_personality_summary()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)