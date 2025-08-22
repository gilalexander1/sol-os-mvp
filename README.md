# Sol OS MVP - ADHD AI Companion

*Security-first ADHD productivity companion with Sol's distinctive personality*

## Overview

Sol OS MVP is a simplified but complete implementation of an ADHD AI companion featuring:

- **Sol's Distinctive Personality**: Existential, broody, thoughtful, and witty AI companion
- **Security-First Architecture**: End-to-end encryption, GDPR compliance, audit logging
- **ADHD-Optimized Features**: Visual time-blocking, task breakdown, mood/energy tracking
- **Real-time Chat**: WebSocket-based conversation with persistent memory
- **Performance Targets**: <2s conversation processing, <500ms mood logging

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- OpenAI API key

### 1. Environment Setup

```bash
# Navigate to project
cd /Users/gman/gil-dev-ecosystem/projects/sol-os-mvp

# Copy environment configuration
cp backend/.env.example backend/.env

# Edit .env file with your actual values:
# - DATABASE_URL (PostgreSQL connection)
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
# - DATA_ENCRYPTION_MASTER_KEY (generate with: openssl rand -hex 64)
# - OPENAI_API_KEY (from OpenAI dashboard)
```

### 2. Database Setup

```bash
# Start shared infrastructure
cd /Users/gman/gil-dev-ecosystem
docker-compose -f infrastructure/docker/docker-compose.yml up -d postgres redis

# Verify database is running
docker ps | grep postgres
```

### 3. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if alembic is configured)
# alembic upgrade head

# Start development server
uvicorn main:app --reload --port 8003
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Verify Installation

Visit:
- Backend API: http://localhost:8003 (should show Sol OS MVP info)
- Frontend: http://localhost:3000 (React development server)
- API Docs: http://localhost:8003/docs (FastAPI interactive documentation)

## Architecture Overview

### Security-First Design

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │───▶│   (FastAPI)     │───▶│   (PostgreSQL)  │
│                 │    │                 │    │                 │
│ • ADHD UI       │    │ • Authentication│    │ • Encrypted     │
│ • Focus Theme   │    │ • Encryption    │    │ • Audit Logs    │
│ • Real-time     │    │ • Sol Engine    │    │ • GDPR Ready    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Services

1. **Sol Personality Engine** - Distinctive AI companion voice
2. **Conversation Memory Service** - Encrypted persistent conversations
3. **Security Services** - Authentication, encryption, audit logging
4. **ADHD Support Services** - Task management, mood tracking, time-blocking

### Enhanced Database Schema

```sql
Users:
- id (UUID, Primary Key)
- email_hash (indexed for privacy)
- email_encrypted (actual email, encrypted)
- username (unique)
- password_hash (bcrypt with high rounds)
- encryption_salt (per-user encryption)
- consent_* (GDPR compliance fields)
- security fields (failed_login_attempts, etc.)

Conversations:
- id (UUID, Primary Key)
- user_id (Foreign Key)
- message_content_encrypted
- sol_response_encrypted
- encryption_key_id
- conversation_type

MoodEnergyLogs:
- id (UUID, Primary Key)  
- user_id (Foreign Key)
- mood_rating (1-5)
- energy_level (1-5)
- time_of_day, day_of_week
- notes_encrypted (optional)

Tasks:
- id (UUID, Primary Key)
- user_id (Foreign Key)
- title, description
- breakdown_steps (JSONB)
- status, priority
- scheduled_start, scheduled_end

SecurityAuditLogs:
- event_type, user_id
- ip_address, user_agent
- success, risk_level
- event_details (JSONB)
```

## 🔧 Development

### Adding New Features
1. **Backend**: Add routes in `main.py`, models in `models.py`, schemas in `schemas.py`
2. **Frontend**: Create components in `src/components/`, pages in `src/app/`
3. **Database**: Use Alembic for migrations: `alembic revision --autogenerate -m "description"`

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `REDIS_URL`: Redis connection string

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up --build -d
```

### Production Considerations
- Set `SECRET_KEY` to a secure random value
- Use environment-specific database credentials
- Configure proper CORS origins
- Enable HTTPS/SSL certificates
- Set up monitoring and logging

## 📁 Project Structure
```
sol-os-mvp/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # Authentication logic
│   ├── database.py       # Database configuration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js 15 app directory
│   │   └── components/   # React components
│   ├── package.json
│   └── tailwind.config.ts
├── docker-compose.yml
└── README.md
```

## 🤝 Contributing

This project was generated from the DevOps Sandbox FastAPI + Next.js template.
Customize as needed for your specific use case.

---

**Built with 💜 by Gil's DevOps Sandbox**