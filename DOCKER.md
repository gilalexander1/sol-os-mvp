# Sol OS MVP - Docker Setup Guide

## 🐳 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key

### 1. Environment Setup
```bash
# Copy environment template
cp .env.docker .env

# Edit .env file with your values:
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
# - DATA_ENCRYPTION_MASTER_KEY (generate with: openssl rand -hex 64) 
# - OPENAI_API_KEY (from OpenAI dashboard)
```

### 2. Generate Secure Keys
```bash
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "DATA_ENCRYPTION_MASTER_KEY=$(openssl rand -hex 64)" >> .env
echo "OPENAI_API_KEY=your-openai-key-here" >> .env
```

### 3. Build and Start
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 4. Access Sol OS
- **Sol OS**: http://localhost:3001
- **Backend API**: http://localhost:8004
- **API Docs**: http://localhost:8004/docs

### 5. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

## 🔧 Development with Docker

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild After Changes
```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Restart services
docker-compose restart
```

### Database Management
```bash
# Access backend container
docker-compose exec backend bash

# View database file
ls -la /app/data/

# SQLite CLI (if needed)
docker-compose exec backend sqlite3 /app/data/sol_os_mvp.db
```

## 📋 Container Details

### Backend Container
- **Port**: 8004
- **Database**: SQLite in persistent volume
- **Health Check**: `/health` endpoint
- **Restart Policy**: unless-stopped

### Frontend Container  
- **Port**: 3001
- **Build**: Next.js standalone mode
- **API Proxy**: Connects to backend container
- **Health Check**: Root endpoint

### Volumes
- `backend_data`: Persistent SQLite database storage

### Network
- `sol_network`: Bridge network for service communication

## 🚀 Production Deployment

For production deployment:

1. **Use production-grade secrets**:
   ```bash
   JWT_SECRET_KEY=$(openssl rand -hex 32)
   DATA_ENCRYPTION_MASTER_KEY=$(openssl rand -hex 64)
   ```

2. **Add HTTPS reverse proxy** (nginx, traefik)

3. **Monitor container health**:
   ```bash
   docker-compose ps
   ```

4. **Backup database volume**:
   ```bash
   docker run --rm -v sol-os-mvp_backend_data:/data -v $(pwd):/backup alpine tar czf /backup/sol-os-backup.tar.gz /data
   ```

## 🧠 Using Sol OS

Once running, Sol OS provides:
- **ADHD-friendly chat** with Sol's existential personality
- **Focus timer** with Pomodoro and custom sessions
- **Task breakdown** for manageable productivity
- **Secure, encrypted** user data storage

Your ADHD AI companion is ready! 🎯