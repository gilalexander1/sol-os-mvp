# Sol OS MVP - Vercel Deployment Guide

## 🚀 Quick Deploy to Vercel

### Prerequisites
- Vercel account (free tier works)
- GitHub repository with this project
- OpenAI API key
- PostgreSQL database (Vercel Postgres recommended)

### 1. Environment Variables Setup

In your Vercel dashboard, configure these environment variables:

```bash
# Required Variables
DATABASE_URL=postgresql://username:password@hostname:port/database_name
OPENAI_API_KEY=sk-your-openai-api-key-here
JWT_SECRET_KEY=your-32-character-jwt-secret-key-here
ENCRYPTION_KEY=your-64-character-encryption-key-here

# Optional
NODE_ENV=production
ENVIRONMENT=production
```

### 2. Database Setup

#### Option A: Vercel Postgres (Recommended)
1. In Vercel dashboard, go to Storage → Create Database
2. Select PostgreSQL
3. Copy the connection string to `DATABASE_URL`

#### Option B: External PostgreSQL
Use any PostgreSQL provider (Supabase, Railway, etc.)

### 3. Generate Secure Keys

```bash
# Generate JWT Secret (32 characters)
openssl rand -hex 32

# Generate Encryption Key (64 characters)  
openssl rand -hex 64
```

### 4. Deploy Commands

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
cd /path/to/sol-os-mvp
vercel --prod

# Or connect via GitHub and deploy automatically
```

### 5. Post-Deployment

1. **Database Migration**: Run database migrations on first deploy
2. **Domain Setup**: Configure custom domain if needed
3. **Monitoring**: Check Vercel Functions logs

## 🏗️ Architecture

- **Frontend**: Next.js deployed to Vercel Edge Network
- **Backend**: FastAPI serverless functions on Vercel
- **Database**: PostgreSQL (Vercel Postgres or external)
- **Authentication**: JWT with secure encryption
- **AI Integration**: OpenAI API for Sol personality

## 🔧 Local Development

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

## 📊 Performance Notes

- Serverless functions have cold starts (~1-2s first request)
- Database connections are pooled for efficiency
- Frontend is cached globally on Vercel CDN
- API responses under 1MB recommended for serverless

## 🔒 Security Features

- JWT token authentication
- Data encryption at rest
- Rate limiting on API endpoints
- CORS configured for production domains
- GDPR compliance built-in