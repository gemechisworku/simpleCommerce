# simpleCommerce Backend

FastAPI backend application for the simpleCommerce platform.

## Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   └── v1/          # API version 1
│   ├── services/         # Business logic
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic schemas
│   ├── utils/            # Utility functions
│   ├── core/             # Core configuration
│   └── migrations/       # Alembic migrations
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker image
└── alembic.ini          # Alembic configuration
```

## Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- API Base: `/api/v1`
- Documentation: `/docs` (Swagger UI)
- ReDoc: `/redoc`
- Health Check: `/health`

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

See `.env.example` for all available environment variables.

