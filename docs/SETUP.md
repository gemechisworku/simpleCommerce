# Setup Guide

This guide provides detailed setup instructions for the simpleCommerce platform.

## Prerequisites

- Docker and Docker Compose installed
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

## Docker Setup (Recommended)

### 1. Clone Repository
```bash
git clone <repository-url>
cd simpleCommerce
```

### 2. Environment Configuration

Create environment files:

**Backend:**
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your configuration:
```env
DATABASE_URL=postgresql://simplecommerce:simplecommerce@db:5432/simplecommerce
JWT_SECRET_KEY=your-secret-key-here
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

**Frontend:**
```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- MinIO object storage
- FastAPI backend
- React frontend

### 4. Initialize Database

```bash
# Enter backend container
docker exec -it simplecommerce_backend bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

### 5. Access Services

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## Local Development Setup

### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   - Ensure PostgreSQL is running
   - Update `DATABASE_URL` in `.env`
   - Run migrations: `alembic upgrade head`

4. **Start server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database credentials

### Port Conflicts

If ports are already in use, modify ports in `docker-compose.yml`:
- Backend: `BACKEND_PORT`
- Frontend: `FRONTEND_PORT`
- Database: `DB_PORT`

### MinIO Setup

1. Access MinIO Console: http://localhost:9001
2. Login with credentials from `.env`
3. Create bucket: `simplecommerce-uploads`
4. Set bucket policy for public read (if needed)

## Next Steps

1. Review specifications in `specs/` directory
2. Check API documentation at `/docs`
3. Start implementing features according to specifications

