# Technical Preferences - Gil's Development Ecosystem
*Comprehensive technical requirements and patterns for all projects*

## Core Technology Stack

### Backend Preferences
- **Framework**: FastAPI (primary), Flask (secondary)
- **Language**: Python 3.11+ with type hints
- **Database**: PostgreSQL 15+ with SQLAlchemy ORM
- **Caching**: Redis for sessions and frequent data
- **Background Tasks**: Celery with Redis broker
- **Authentication**: JWT with secure refresh tokens
- **API Documentation**: Automatic OpenAPI/Swagger generation

### Frontend Preferences  
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS 4+ with custom design systems
- **State Management**: React Context + React Query/SWR
- **UI Components**: Custom components with shared design system
- **Animation**: Framer Motion for smooth interactions
- **Forms**: React Hook Form with validation

### Infrastructure Preferences
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for development
- **Database**: Shared PostgreSQL container
- **Caching**: Shared Redis container  
- **Reverse Proxy**: Nginx for production
- **Environment Management**: Docker environments with .env files

## Project-Specific Requirements

### Sol OS - ADHD AI Companion
**Special Requirements**: Real-time conversation memory, complex pattern recognition, ADHD-specific UX patterns

#### Backend Architecture
```python
# Core Services Required
- ConversationMemoryEngine: Persistent conversation state across sessions
- PatternRecognitionService: ML-based mood/energy/productivity patterns
- PersonalityEngine: Sol's distinctive voice and response generation
- IntegrationHub: Notion API, Calendar API, Philosopher-Sol API connections
- ADHDSupportServices: Time-boxing, task breakdown, focus management
- ReflectionEngine: Structured prompts and philosophical dialogue
```

#### Frontend Architecture
```typescript
// ADHD-Friendly Components
- AdaptiveDashboard: Context-aware interface that adjusts to focus level
- TimeBlockingCalendar: Visual time management with drag-drop blocks
- QuickCaptureControls: Rapid mood/energy/thought input (sliders, voice)
- FocusEnvironmentController: Adaptive UI, soundscapes, notification management
- CompanionPresence: Simulated body doubling and companion interactions
- ReflectiveDialogue: Philosophical conversation interface with memory
```

#### Database Schema
```sql
-- Conversation Memory (Core Feature)
conversations (
    id: UUID PRIMARY KEY,
    user_id: UUID REFERENCES users(id),
    session_id: VARCHAR,
    message_content: TEXT,
    context_data: JSONB,
    personality_state: JSONB,
    timestamp: TIMESTAMP,
    emotional_context: JSONB
);

-- Mood & Energy Tracking
mood_energy_logs (
    id: UUID PRIMARY KEY,
    user_id: UUID REFERENCES users(id),
    mood_rating: INTEGER,
    energy_level: INTEGER,
    focus_capacity: INTEGER,
    context_tags: VARCHAR[],
    notes: TEXT,
    logged_at: TIMESTAMP
);

-- Task & Productivity Tracking
tasks (
    id: UUID PRIMARY KEY,
    user_id: UUID REFERENCES users(id),
    title: VARCHAR NOT NULL,
    description: TEXT,
    atomic_breakdown: JSONB,
    energy_requirement: INTEGER,
    time_estimate: INTERVAL,
    completed_at: TIMESTAMP,
    focus_sessions: JSONB
);

-- Reflection & Philosophy
reflection_entries (
    id: UUID PRIMARY KEY,
    user_id: UUID REFERENCES users(id),
    prompt_type: VARCHAR,
    content: TEXT,
    philosophical_insights: JSONB,
    linked_conversations: UUID[],
    created_at: TIMESTAMP
);

-- Pattern Learning Data
pattern_data (
    id: UUID PRIMARY KEY,
    user_id: UUID REFERENCES users(id),
    pattern_type: VARCHAR,
    data_points: JSONB,
    correlations: JSONB,
    predictions: JSONB,
    confidence_score: FLOAT,
    updated_at: TIMESTAMP
);
```

#### API Integrations
```python
# Required External Integrations
class NotionIntegration:
    """Seamless journaling sync with Notion workspace"""
    - create_journal_entry()
    - sync_daily_reflections()
    - update_philosophical_database()

class CalendarIntegration:
    """Google Calendar for context-aware scheduling"""
    - read_upcoming_events()
    - suggest_focus_blocks()
    - create_time_boxing_events()

class PhilosopherSolIntegration:
    """Connect to philosopher-sol for ethical insights"""
    - get_ethical_perspective()
    - request_philosophical_dialogue()
    - sync_decision_frameworks()
```

### Philosophers Guide - Travel App
**Theme**: Mindful (earth tones, nature-focused)
**Special Requirements**: Location-based features, travel planning, journaling

#### Specific Technical Needs
- **Geolocation Services**: Maps integration for travel planning
- **Offline Capability**: PWA features for travel without internet
- **Image Handling**: Photo upload and organization for travel memories
- **Currency/Weather APIs**: Travel-specific data integrations

### Philosopher Sol - AI Ethics Tool  
**Theme**: Stoic (classical Greek aesthetic)
**Special Requirements**: Complex decision trees, philosophical framework integration

#### Specific Technical Needs
- **Decision Tree Engine**: Complex logical flow management
- **Philosophy Database**: Comprehensive philosophical knowledge base
- **Framework Comparison**: Side-by-side ethical framework analysis
- **Export Capabilities**: PDF/print-friendly decision summaries

### PIP Claims Tool - Insurance Processing
**Theme**: Professional (business with beach accents)  
**Special Requirements**: Complex business rules, regulatory compliance

#### Specific Technical Needs
- **Business Rules Engine**: Complex claims processing logic
- **Document Processing**: PDF parsing and form handling
- **Audit Trail**: Complete action logging for compliance
- **Regulatory Reporting**: Automated compliance report generation

### Portfolio Site - Professional Showcase
**Theme**: Cosmic (space/glass aesthetic)
**Special Requirements**: Performance optimization, SEO, professional presentation

#### Specific Technical Needs
- **Static Site Generation**: Optimized build for fast loading
- **SEO Optimization**: Meta tags, structured data, sitemap
- **Performance Monitoring**: Core Web Vitals optimization
- **Analytics Integration**: Professional usage tracking

## ADHD-Specific Design Patterns

### Visual Design Requirements
```css
/* ADHD-Friendly Color Palette */
:root {
  --focus-primary: #4A90E2;      /* Calming blue */
  --focus-secondary: #7CB342;    /* Soft green */
  --focus-accent: #FFA726;       /* Warm orange */
  --focus-neutral: #90A4AE;      /* Soft gray */
  --focus-background: #FAFAFA;   /* Off-white */
  --focus-text: #37474F;         /* Dark gray */
}

/* Cognitive Load Reduction */
.adhd-friendly {
  /* Minimal visual noise */
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  
  /* Clear visual hierarchy */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  
  /* Reduced cognitive load */
  max-width: 800px; /* Prevent overwhelming wide layouts */
  padding: 1.5rem;
  margin: 1rem auto;
}
```

### Interaction Patterns
```typescript
// Quick Capture Mechanisms
interface QuickCaptureProps {
  onVoiceInput?: (audio: Blob) => void;
  onTextInput?: (text: string) => void;
  onEmojiSelect?: (emotion: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

// Gentle Notification System  
interface ADHDNotification {
  type: 'gentle' | 'reminder' | 'celebration';
  priority: 'low' | 'medium' | 'high';
  canDefer: boolean;
  contextAware: boolean;
  soundscape?: 'chime' | 'nature' | 'silent';
}

// Focus State Management
interface FocusState {
  level: 'deep' | 'moderate' | 'scattered';
  timeRemaining?: number;
  environment: 'minimal' | 'standard' | 'rich';
  interruptsEnabled: boolean;
}
```

## Development Standards

### Code Quality Requirements
```python
# Python Standards
- Type hints required for all functions
- Docstrings following Google format
- Pytest for testing with >80% coverage
- Black formatter with line length 88
- isort for import organization
- mypy for static type checking

# Example Function Signature
async def process_conversation_memory(
    user_id: UUID,
    message_content: str,
    context: Dict[str, Any],
    personality_state: Optional[PersonalityState] = None
) -> ConversationResponse:
    """
    Process and store conversation with persistent memory.
    
    Args:
        user_id: Unique identifier for the user
        message_content: The user's message text
        context: Additional context data
        personality_state: Current Sol personality state
        
    Returns:
        ConversationResponse with Sol's reply and updated state
        
    Raises:
        ConversationError: If memory processing fails
    """
```

```typescript
// TypeScript Standards
// Strict mode enabled, no implicit any
// Comprehensive interface definitions
// React components with proper typing

interface ConversationMessage {
  id: string;
  content: string;
  role: 'user' | 'sol';
  timestamp: Date;
  emotionalContext?: EmotionalState;
  memoryLinks?: string[];
}

// React Component with ADHD considerations
interface ADHDFriendlyComponentProps {
  focusLevel: FocusLevel;
  cognitiveLoad: 'minimal' | 'standard' | 'high';
  children: React.ReactNode;
  onFocusChange?: (newLevel: FocusLevel) => void;
}
```

### Database Design Patterns
```sql
-- Conversation Memory Pattern (Key for Sol OS)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_id VARCHAR(255) NOT NULL,
    message_content TEXT NOT NULL,
    sol_response TEXT,
    context_data JSONB DEFAULT '{}',
    personality_state JSONB DEFAULT '{}',
    emotional_analysis JSONB DEFAULT '{}',
    memory_connections UUID[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_conversations_user_session ON conversations(user_id, session_id);
CREATE INDEX idx_conversations_timestamp ON conversations(created_at);
CREATE INDEX idx_conversations_memory_connections ON conversations USING GIN(memory_connections);

-- Pattern Recognition Support
CREATE INDEX idx_mood_energy_patterns ON mood_energy_logs(user_id, logged_at, mood_rating, energy_level);
```

### API Design Patterns
```python
# FastAPI Patterns for Sol OS
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ConversationRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class SolResponse(BaseModel):
    response: str
    personality_state: Dict[str, Any]
    emotional_context: Dict[str, Any]
    memory_links: List[str]
    follow_up_suggestions: List[str]

@app.post("/api/v1/conversation", response_model=SolResponse)
async def process_conversation(
    request: ConversationRequest,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> SolResponse:
    """
    Process conversation with Sol's personality engine.
    
    Maintains persistent memory and generates contextually appropriate responses
    with Sol's distinctive voice (existential, broody, thoughtful, witty).
    """
```

### Performance Requirements
```yaml
# Sol OS Performance Targets
response_times:
  conversation_processing: <2s  # Critical for real-time feel
  mood_energy_logging: <500ms  # Must feel instant
  task_breakdown: <1s
  pattern_recognition: <3s     # Background processing acceptable

memory_usage:
  conversation_history: 100MB per user max
  pattern_data: 50MB per user max
  real_time_cache: 10MB per active session

scalability:
  concurrent_users: 1000+ 
  conversation_throughput: 100 req/s
  background_processing: async with Celery
```

## Deployment Patterns

### Development Environment
```yaml
# docker-compose.dev.yml pattern
services:
  app:
    build: .
    volumes:
      - ./:/app  # Hot reload
    environment:
      - DEBUG=true
      - CONVERSATION_MEMORY_DEBUG=true
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sol_os_dev
    volumes:
      - postgres_dev:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_dev:/data
```

### Production Deployment
```yaml
# Optimized for Sol OS real-time requirements
services:
  app:
    image: sol-os:production
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1GB
          cpus: "0.5"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Security Requirements

### Authentication & Authorization
```python
# Sol OS requires persistent sessions for memory continuity
class SecureSessionManager:
    """
    Handle long-lived sessions for conversation memory while maintaining security.
    """
    - refresh_token_rotation: bool = True
    - session_timeout: int = 30 * 24 * 60 * 60  # 30 days for continuity
    - memory_encryption: bool = True  # Encrypt sensitive conversation data
    - audit_conversation_access: bool = True
```

### Data Privacy
- **Conversation Encryption**: All conversation data encrypted at rest
- **Memory Isolation**: User conversations completely isolated  
- **GDPR Compliance**: Complete data export/deletion capabilities
- **Minimal Data Collection**: Only essential data for ADHD support features

## Testing Strategies

### Sol OS Specific Testing
```python
# Conversation Memory Testing
class TestConversationMemory:
    def test_personality_consistency():
        """Ensure Sol's voice remains consistent across conversations"""
        
    def test_memory_persistence():
        """Verify conversations are remembered across sessions"""
        
    def test_adhd_pattern_recognition():
        """Validate pattern detection for mood/energy/focus"""

# ADHD UX Testing  
class TestADHDExperience:
    def test_cognitive_load():
        """Ensure UI doesn't overwhelm users"""
        
    def test_quick_capture():
        """Verify rapid input mechanisms work smoothly"""
        
    def test_gentle_notifications():
        """Ensure notifications are ADHD-friendly"""
```

This comprehensive technical specification ensures Sol OS will be built exactly as envisioned - a sophisticated ADHD companion with philosophical depth, persistent memory, and Sol's distinctive personality.