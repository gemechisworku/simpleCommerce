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
   - Frontend: http://localhost:3001 (or `FRONTEND_PORT` if set)
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

## Admin Dashboard & Configuration

### Accessing the admin dashboard

1. **URL:** Open **http://localhost:3001/admin** (use your frontend port if different).
2. **Login:** You must be logged in with a **sales** or **admin** role. Customer accounts cannot access `/admin`.

### First-time setup: create an admin user

To get your first admin account, seed the database (creates a default admin and optional mock data):

```bash
cd backend
# With venv activated, or from project root with Docker:
docker compose exec backend python -m scripts.seed_mock_data
```

**Default seeded admin (development):**
- **Phone:** `+251911111111` (override with `SUPERADMIN_PHONE`)
- **OTP in dev:** After you click “Request OTP” on the login page, the 6-digit code is printed in the **backend container logs** (e.g. `docker compose logs -f backend`). Use that code to verify and log in.

Then:

1. Go to **http://localhost:3001/login**
2. Enter phone `+251911111111` (or your `SUPERADMIN_PHONE`)
3. Click **Request OTP**, then check backend logs for the OTP code
4. Enter the code and log in
5. Open **http://localhost:3001/admin** or click **Store** in the header and use the admin nav

### Where to configure things (admin UI)

| What to configure | Where in admin |
|-------------------|----------------|
| **Dashboard** (metrics, recent orders) | `/admin` |
| **Orders** (list, detail, status, cancel) | **Orders** |
| **Payment queue** (approve / reject / request resubmit) | **Payments** |
| **Products** (list, create, edit, delete, variants, images) | **Products** |
| **Categories** | **Categories** |
| **Delivery zones** (fees, ETA) | **Delivery Zones** |
| **Payment methods** (bank, mobile money, etc.) | **Payment Methods** |
| **Users** (create sales/admin, change roles) | **Users** (admin role only) |

### Optional: customize seeded admin

Set before running the seed script:

- `SUPERADMIN_PHONE` – phone number (e.g. `+251912345678`)
- `SUPERADMIN_EMAIL` – email (optional)
- `SUPERADMIN_FIRST_NAME` / `SUPERADMIN_LAST_NAME` – display name

## Environment Variables

### Backend (.env)

See `backend/.env.example` for all available environment variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key
- `TELEGRAM_BOT_TOKEN`: Bot token for Telegram Mini App auth (optional)

### Frontend (.env)

- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_ENVIRONMENT`: Environment (development/production)

## Telegram Mini App

The same frontend can run inside Telegram as a **Mini App**. Users open the app from your bot (menu button or link); they are auto-logged in with their Telegram account. No extra build is required.

**Setup:** Create a bot with [@BotFather](https://t.me/BotFather), set `TELEGRAM_BOT_TOKEN` in the backend, deploy the frontend to a **public HTTPS** URL, then in BotFather set the **Menu button URL** to that URL. Full steps: [docs/TELEGRAM_MINI_APP.md](docs/TELEGRAM_MINI_APP.md).

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

