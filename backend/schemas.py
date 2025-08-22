"""
Pydantic schemas for Sol OS MVP
Request/response models for API endpoints
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# Authentication schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    google_calendar_connected: bool = False
    google_calendar_sync_enabled: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Task schemas
class TaskCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    category: Optional[str] = Field(None, max_length=50)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    category: Optional[str] = Field(None, max_length=50)
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_broken_down: Optional[bool] = None
    breakdown_steps: Optional[List[str]] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    category: Optional[str]
    completion_percentage: int
    is_broken_down: bool
    breakdown_steps: List[str]
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# Time Block schemas
class TimeBlockCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    block_type: str = Field("work", pattern="^(work|personal|rest|focus|external)$")
    color: str = Field("#4A90E2", pattern="^#[0-9A-Fa-f]{6}$")
    is_flexible: bool = False
    buffer_time_minutes: int = Field(10, ge=0, le=60)
    linked_task_id: Optional[str] = None
    google_calendar_sync_enabled: bool = True

class TimeBlockUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    block_type: Optional[str] = Field(None, pattern="^(work|personal|rest|focus|external)$")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    is_flexible: Optional[bool] = None
    buffer_time_minutes: Optional[int] = Field(None, ge=0, le=60)
    linked_task_id: Optional[str] = None
    google_calendar_sync_enabled: Optional[bool] = None

class TimeBlockResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    location: Optional[str]
    start_time: datetime
    end_time: datetime
    all_day: bool
    block_type: str
    color: str
    is_flexible: bool
    buffer_time_minutes: int
    linked_task_id: Optional[str]
    google_calendar_event_id: Optional[str]
    google_calendar_sync_enabled: bool
    sync_status: str
    sync_error: Optional[str]
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Focus Session schemas
class FocusSessionCreate(BaseModel):
    task_id: Optional[str] = None
    session_type: str = Field("pomodoro", pattern="^(pomodoro|custom)$")
    planned_duration: int = Field(..., ge=5, le=480)  # 5 minutes to 8 hours

class FocusSessionUpdate(BaseModel):
    ended_at: Optional[datetime] = None
    completed: Optional[bool] = None
    interruptions: Optional[int] = Field(None, ge=0)
    focus_rating: Optional[int] = Field(None, ge=1, le=5)
    productivity_rating: Optional[int] = Field(None, ge=1, le=5)

class FocusSessionResponse(BaseModel):
    id: str
    task_id: Optional[str]
    session_type: str
    planned_duration: int
    actual_duration: Optional[int]
    started_at: datetime
    ended_at: Optional[datetime]
    completed: bool
    interruptions: int
    focus_rating: Optional[int]
    productivity_rating: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# Mood Energy Log schemas
class MoodEnergyLogCreate(BaseModel):
    mood_rating: int = Field(..., ge=1, le=5)
    energy_level: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None
    time_of_day: str = Field("morning", pattern="^(morning|afternoon|evening)$")
    input_method: str = Field("tap", pattern="^(tap|voice|emoji)$")

class MoodEnergyLogResponse(BaseModel):
    id: str
    mood_rating: int
    energy_level: int
    notes: Optional[str]
    time_of_day: str
    day_of_week: int
    input_method: str
    logged_at: datetime

    class Config:
        from_attributes = True

# Chat schemas
class ChatMessage(BaseModel):
    message: str = Field(..., max_length=2000)
    conversation_type: str = Field("general", pattern="^(general|productivity|mood|planning)$")

class ChatResponse(BaseModel):
    id: str
    user_message: str
    sol_response: str
    conversation_type: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Google Calendar schemas
class CalendarSyncStatus(BaseModel):
    connected: bool
    sync_enabled: bool
    last_sync: Optional[datetime]

class CalendarAuthResponse(BaseModel):
    auth_url: str

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Health check schema
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"