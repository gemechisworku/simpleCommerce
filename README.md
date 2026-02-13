# simpleCommerce

Commerce & Order Operations Platform - A centralized e-commerce platform for managing product catalogs, customer orders, and manual payment workflows with screenshot-based payment verification.

## Project Overview

simpleCommerce is a full-stack e-commerce platform built with:
- **Frontend:** ReactJS (SPA) with TypeScript
- **Backend:** FastAPI (Python) with Uvicorn
- **Database:** PostgreSQL with SQLAlchemy + Alembic
- **Storage:** MinIO (S3-compatible) for file storage
- **Infrastructure:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (production)

## Architecture

The system follows a **microservice-ish monolith** architecture:
- Single codebase with modular components
- Monolithic deployment for simplicity
- Clear separation of concerns through logical modules
- Designed to support future service extraction if needed

## Project Structure

```
simpleCommerce/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/     # Business logic
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── utils/        # Utility functions
│   │   ├── core/         # Core configuration
│   │   └── migrations/   # Alembic migrations
│   ├── tests/            # Test files
│   ├── Dockerfile       # Backend Docker image
│   └── requirements.txt # Python dependencies
│
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── hooks/       # Custom React hooks
│   │   ├── utils/       # Utility functions
│   │   ├── types/       # TypeScript types
│   │   ├── theme/       # Theme configuration
│   │   └── constants/   # Constants
│   ├── public/          # Static files
│   ├── Dockerfile       # Frontend Docker image (dev)
│   └── package.json     # Node dependencies
│
├── nginx/               # Nginx configuration
├── docker/              # Docker-related files
├── scripts/             # Utility scripts
├── docs/                # Documentation
├── specs/               # Project specifications
└── docker-compose.yml   # Docker Compose configuration
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd simpleCommerce
   ```

2. **Set up environment variables**
   ```bash
   # Copy example env files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Edit .env files with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001

### Local Development

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

4. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

## Environment Variables

### Backend (.env)

See `backend/.env.example` for all available environment variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key

### Frontend (.env)

- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_ENVIRONMENT`: Environment (development/production)

## API Documentation

Once the backend is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Code Quality

```bash
# Backend formatting
cd backend
black .
flake8 .

# Frontend formatting
cd frontend
npm run format
npm run lint
```

## Specifications

All project specifications are located in the `specs/` directory:
- `_meta.md`: Architectural principles and constraints
- `functional_requirements.md`: User stories and acceptance criteria
- `api_contracts.md`: API endpoints and contracts
- `database_design.md`: Database schema and design
- `ui_components_design.md`: UI component specifications
- `architecture_design.md`: System architecture details

## Contributing

1. Read the specifications in `specs/` directory
2. Follow the coding standards defined in `specs/_meta.md`
3. Create feature branches from `main`
4. Write tests for new features
5. Submit pull requests

## License

[Add your license here]

## Support

For questions or issues, please refer to the specifications or create an issue in the repository.

