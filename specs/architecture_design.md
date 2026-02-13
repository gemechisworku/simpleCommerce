# Architecture Design Document

**Project Name:** Melegna Foods Commerce & Order Operations Platform  
**Version:** 1.0  
**Based on:** Software Requirements Specification v1.0

---

## 1. System Architecture Overview

### 1.1 Architecture Pattern

The system follows a **microservice-ish monolith** architecture pattern:
- Single codebase with modular components
- Monolithic deployment for simplicity (single-server baseline)
- Clear separation of concerns through logical modules
- Designed to support future service extraction if needed

### 1.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
├─────────────────────────────────────────────────────────────┤
│  Web App (React SPA)          │  Telegram Mini App (Future) │
│  - Customer Storefront        │  - Same React app           │
│  - Admin Dashboard             │  - Telegram WebApp wrapper  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Reverse Proxy (Nginx)                     │
│                    - HTTPS termination                      │
│                    - Static file serving                    │
│                    - Request routing                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Auth Service                                         │  │
│  │  - Phone OTP                                          │  │
│  │  - Email login                                        │  │
│  │  - Telegram auth                                      │  │
│  │  - JWT token management                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Product Catalog Service                              │  │
│  │  - Product management                                 │  │
│  │  - Inventory tracking                                 │  │
│  │  - Category management                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Order & Payment Workflow Engine                      │  │
│  │  - Order creation                                     │  │
│  │  - Payment submission                                 │  │
│  │  - Status state machine                               │  │
│  │  - Delivery zone calculation                          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  File Upload Service                                  │  │
│  │  - Payment screenshot upload                          │  │
│  │  - Image validation                                   │  │
│  │  - Storage integration                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Notification Layer                                   │  │
│  │  - In-app notifications                               │  │
│  │  - Telegram notifications (future)                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Admin Service                                        │  │
│  │  - Payment review queue                               │  │
│  │  - Order management                                   │  │
│  │  - Reporting                                          │  │
│  │  - Configuration management                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    MinIO     │    │  Background  │
│  Database    │    │  (S3-compat) │    │  Jobs (opt)  │
│              │    │              │    │  Celery/RQ   │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 1.3 Technology Stack

#### Frontend
- **Framework:** ReactJS (SPA)
- **UI Approach:** Mobile-first responsive design
- **State Management:** (To be decided during implementation)
- **Build Tool:** (To be decided during implementation)

#### Backend
- **Framework:** FastAPI (Python)
- **ASGI Server:** Uvicorn
- **API Style:** RESTful
- **Background Jobs:** Celery/RQ (optional for v1)

#### Database
- **Primary DB:** PostgreSQL
- **ORM/Migrations:** SQLAlchemy + Alembic

#### Storage
- **Object Storage:** MinIO (S3-compatible) in Docker
- **Alternative:** Local volume for development
- **Future:** External S3 for production

#### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (production)
- **Environment Management:** `.env` files with compose overrides

---

## 2. Component Architecture

### 2.1 Customer Storefront Component

**Purpose:** Primary interface for customers to browse products and place orders.

**Responsibilities:**
- Product catalog browsing (list, detail, search, filter)
- Shopping cart management
- Order placement (checkout flow)
- Payment instruction display
- Payment screenshot upload
- Order tracking and status viewing
- User account management

**Key Features:**
- Mobile-first responsive design
- Real-time stock availability display
- Delivery zone selection and fee calculation
- Payment method display with copyable account details

### 2.2 Admin Dashboard Component

**Purpose:** Internal interface for Sales and Admin users to manage operations.

**Responsibilities:**
- Order management and status updates
- Payment review queue
- Product catalog management
- Inventory management
- Payment methods configuration
- Delivery zones and fees configuration
- User and role management
- Reporting and analytics

**Key Features:**
- Payment screenshot inline viewing
- One-click approve/reject actions
- Order status state machine enforcement
- Filterable order lists
- Dashboard analytics

### 2.3 Order & Payment Workflow Engine

**Purpose:** Core business logic for order lifecycle and payment processing.

**Responsibilities:**
- Order creation and validation
- Stock reservation (on order placement or payment approval - configurable)
- Order status state machine management
- Delivery fee calculation based on zones
- Expected delivery date calculation
- Payment submission handling
- Payment status transitions
- Order cancellation logic

**State Machine:**
```
PENDING_PAYMENT → PAYMENT_SUBMITTED → PAYMENT_RESUBMIT_REQUESTED
                                              ↓
                                    PAYMENT_REJECTED
                                              ↓
                                    PAID → PACKING → DISPATCHED → DELIVERED
                                              ↓
                                    CANCELLED (anytime by Sales/Admin)
```

### 2.4 Auth Service

**Purpose:** Authentication and authorization management.

**Responsibilities:**
- Phone OTP generation and verification
- Email login (magic link or OTP - to be decided)
- Telegram initData signature validation
- Account linking (phone + email + telegram_user_id)
- JWT token generation and refresh
- Role-based access control (RBAC)
- Session management

**Authentication Flows:**
1. **Phone OTP:** Request OTP → Verify OTP → Issue JWT tokens
2. **Email:** Request magic link/OTP → Verify → Issue JWT tokens
3. **Telegram:** Validate initData → Link to existing account or create → Issue JWT tokens

### 2.5 File Upload Service

**Purpose:** Handle payment screenshot uploads and storage.

**Responsibilities:**
- File upload endpoint (multipart/form-data)
- Image validation (type, size limits)
- Secure file storage in MinIO/S3
- File URL generation for retrieval
- Optional image processing/optimization

**Security:**
- File type validation (jpg/png only)
- Size limits enforcement
- Virus scanning (optional, future)

### 2.6 Notification Layer

**Purpose:** In-app and external notifications.

**Responsibilities:**
- In-app notification creation and delivery
- Notification storage in database
- Real-time notification updates (WebSocket/SSE - to be decided)
- Telegram bot notifications (future, behind feature flag)

**Notification Types:**
- Customer: Payment approved/rejected, order status updates, delivery updates
- Sales/Admin: New order, new payment submitted

---

## 3. Database Architecture

### 3.1 Database Schema Overview

The database follows a relational model with the following core entities:

#### Core Entities

1. **users** - User accounts with multi-identity support
2. **products** - Product catalog
3. **product_variants** - Product variants with pricing and stock
4. **product_images** - Product image URLs
5. **orders** - Order records
6. **order_items** - Order line items
7. **payment_methods** - Admin-configured payment options
8. **payments** - Payment submissions and reviews
9. **order_status_history** - Audit trail for status changes
10. **delivery_zones** - Delivery zone configuration

### 3.2 Entity Relationships

```
users (1) ────< (N) orders
orders (1) ────< (N) order_items
orders (1) ────< (N) payments
orders (1) ────< (N) order_status_history
products (1) ────< (N) product_variants
products (1) ────< (N) product_images
products (1) ────< (N) order_items
product_variants (1) ────< (N) order_items
payment_methods (1) ────< (N) payments
delivery_zones (1) ────< (N) orders
users (1) ────< (N) payments (as reviewed_by)
```

### 3.3 Key Design Decisions

- **UUID Primary Keys:** Used for `users` and potentially other entities for security and distributed system readiness
- **Soft Deletes:** Recommended for products (using `is_active` flag or `deleted_at` timestamp)
- **Audit Trail:** `order_status_history` table tracks all status transitions with actor and timestamp
- **Stock Management:** Stock quantity stored at variant level; reservation strategy configurable
- **Multi-Identity:** Users can have phone, email, and telegram_user_id (all unique when present)

### 3.4 Indexing Strategy

**Recommended Indexes:**
- `users.phone` (unique, verified users)
- `users.email` (unique, verified users)
- `users.telegram_user_id` (unique)
- `orders.user_id` (for customer order queries)
- `orders.status` (for filtering and queue management)
- `orders.created_at` (for date-based queries)
- `payments.status` (for payment queue)
- `payments.order_id` (for order-payment joins)
- `product_variants.product_id` (for product detail queries)
- `order_items.order_id` (for order detail queries)

---

## 4. API Architecture

### 4.1 API Design Principles

- **RESTful:** Follow REST conventions
- **Stateless:** Each request contains all necessary information
- **Versioned:** API versioning strategy (to be decided: URL path vs header)
- **Documented:** OpenAPI/Swagger documentation
- **Secure:** All endpoints require authentication except public product browsing

### 4.2 API Structure

#### Base URL Structure
```
/api/v1/
```

#### Endpoint Categories

**4.2.1 Authentication Endpoints** (`/auth/*`)
- `POST /auth/otp/request` - Request phone OTP
- `POST /auth/otp/verify` - Verify phone OTP and get tokens
- `POST /auth/email/request` - Request email magic link/OTP
- `POST /auth/email/verify` - Verify email and get tokens
- `POST /auth/telegram/verify` - Verify Telegram initData and link account
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Invalidate refresh token

**4.2.2 Customer Endpoints** (`/products/*`, `/orders/*`, `/cart/*`)
- `GET /products` - List products (public, with pagination/filtering)
- `GET /products/{id}` - Product detail (public)
- `POST /cart/checkout` - Create order from cart
- `GET /orders/my` - List customer's orders
- `GET /orders/{id}` - Order detail (customer-owned only)
- `POST /orders/{id}/payment` - Upload payment screenshot
- `POST /orders/{id}/cancel` - Cancel order (if allowed)

**4.2.3 Admin/Sales Endpoints** (`/admin/*`)
- `GET /admin/orders` - List all orders (with filters)
- `GET /admin/orders/{id}` - Order detail (any order)
- `POST /admin/orders/{id}/status` - Update order status
- `GET /admin/payments/queue` - Payment review queue
- `POST /admin/payments/{id}/approve` - Approve payment
- `POST /admin/payments/{id}/reject` - Reject payment
- `POST /admin/payments/{id}/resubmit_request` - Request resubmission

**4.2.4 Admin Configuration Endpoints** (`/admin/*`)
- CRUD for products, variants, inventory, categories
- CRUD for payment methods
- CRUD for delivery zones
- CRUD for users and roles

### 4.3 Authentication & Authorization

**Authentication:**
- JWT-based authentication
- Access token (short-lived, e.g., 15 minutes)
- Refresh token (longer-lived, e.g., 7 days)
- Tokens stored in HTTP-only cookies or Authorization header

**Authorization:**
- Role-based access control (RBAC)
- Roles: `customer`, `sales`, `admin`
- Endpoint-level role checks
- Resource-level ownership checks (e.g., customers can only view their own orders)

### 4.4 Request/Response Format

**Request:**
- JSON body for POST/PUT requests
- Query parameters for filtering/pagination
- Multipart/form-data for file uploads

**Response:**
- JSON format
- Standardized error response format
- Pagination metadata for list endpoints

**Example Response Structure:**
```json
{
  "data": { ... },
  "meta": {
    "pagination": { ... }
  }
}
```

**Example Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [ ... ]
  }
}
```

---

## 5. Deployment Architecture

### 5.1 Docker Services

The system is containerized using Docker Compose with the following services:

#### 5.1.1 Frontend Service
- **Image:** Node.js-based React build
- **Port:** 3000 (dev) / 80 (prod via nginx)
- **Volumes:** Source code mount (dev) / Built static files (prod)
- **Environment:** API base URL, feature flags

#### 5.1.2 Backend Service
- **Image:** Python with FastAPI + Uvicorn
- **Port:** 8000 (internal)
- **Dependencies:** Database, MinIO
- **Environment:** Database URL, JWT secrets, OTP keys, storage keys, Telegram keys
- **Health Check:** `/health` endpoint

#### 5.1.3 Database Service
- **Image:** PostgreSQL (latest stable)
- **Port:** 5432 (internal)
- **Volumes:** Data persistence volume
- **Environment:** Database name, user, password
- **Init Scripts:** Alembic migrations on startup

#### 5.1.4 Storage Service (MinIO)
- **Image:** MinIO (S3-compatible)
- **Port:** 9000 (API), 9001 (Console)
- **Volumes:** Storage data volume
- **Environment:** Access key, secret key, bucket configuration
- **Initialization:** Optional init container for bucket creation

#### 5.1.5 Nginx Service (Production)
- **Image:** Nginx
- **Port:** 80 (HTTP), 443 (HTTPS)
- **Configuration:** Reverse proxy, SSL termination, static file serving
- **SSL:** Let's Encrypt or custom certificates

### 5.2 Docker Compose Structure

```
docker-compose.yml (base)
├── docker-compose.dev.yml (development overrides)
└── docker-compose.prod.yml (production overrides)
```

**Development:**
- Hot reload for frontend and backend
- Direct port exposure
- Development database with seed data option
- Local MinIO or file system storage

**Production:**
- Optimized builds
- Nginx reverse proxy
- SSL/TLS configuration
- Production database settings
- External MinIO or S3

### 5.3 Environment Configuration

**Environment Variables (.env):**

```bash
# Database
DATABASE_URL=postgresql://user:pass@db:5432/melegna
POSTGRES_DB=melegna
POSTGRES_USER=melegna_user
POSTGRES_PASSWORD=...

# JWT
JWT_SECRET_KEY=...
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OTP Provider
OTP_PROVIDER=dev|sms_gateway|telegram
OTP_SMS_API_KEY=...
OTP_SMS_API_SECRET=...

# Storage
STORAGE_TYPE=minio|s3
MINIO_ENDPOINT=storage:9000
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
MINIO_BUCKET_NAME=payments
S3_ENDPOINT_URL=... (if using S3)
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...

# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBAPP_SECRET=...

# Application
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development|production
```

---

## 6. Security Architecture

### 6.1 Authentication Security

- **JWT Tokens:**
  - Short-lived access tokens (15 minutes)
  - Longer-lived refresh tokens (7 days)
  - Secure token storage (HTTP-only cookies recommended)
  - Token rotation on refresh

- **OTP Security:**
  - Rate limiting per phone number/IP address
  - OTP expiration (e.g., 5 minutes)
  - OTP single-use enforcement
  - Dev mode OTP for non-production environments

- **Telegram Auth:**
  - Server-side initData signature validation
  - Timestamp validation to prevent replay attacks
  - Secure hash verification using Telegram secret

### 6.2 Authorization Security

- **RBAC Enforcement:**
  - Server-side role checks on every request
  - Role claims in JWT tokens
  - Resource-level ownership validation
  - Admin-only endpoints protected

- **State Machine Security:**
  - Invalid status transitions blocked server-side
  - Status change permissions enforced by role
  - Audit trail for all status changes

### 6.3 Data Security

- **HTTPS:**
  - All production traffic over HTTPS
  - SSL/TLS certificate management
  - HSTS headers

- **Input Validation:**
  - Request validation using Pydantic models
  - SQL injection prevention (ORM parameterized queries)
  - XSS prevention (input sanitization, CSP headers)

- **File Upload Security:**
  - File type validation (whitelist: jpg, png)
  - File size limits
  - Secure file storage (not in web root)
  - Optional virus scanning

- **Database Security:**
  - Parameterized queries only
  - Database user with minimal privileges
  - Connection encryption (SSL)

### 6.4 Rate Limiting

- OTP request rate limiting (per phone/IP)
- API endpoint rate limiting (per user/IP)
- File upload rate limiting

---

## 7. Data Flow Architecture

### 7.1 Order Placement Flow

```
Customer → Frontend → Backend API
                        ↓
                   Validate Cart
                   Check Stock
                   Calculate Delivery Fee
                   Create Order (PENDING_PAYMENT)
                   Reserve Stock (if configured)
                        ↓
                   Return Order Details
                        ↓
Frontend → Display Payment Instructions
```

### 7.2 Payment Submission Flow

```
Customer → Frontend → Upload Screenshot
                        ↓
                   Backend API
                        ↓
                   Validate File
                   Store in MinIO
                   Create Payment Record
                   Update Order (PAYMENT_SUBMITTED)
                        ↓
                   Create Notification
                        ↓
Sales/Admin Dashboard → Payment Queue
```

### 7.3 Payment Review Flow

```
Sales/Admin → View Payment Queue
                ↓
           Select Payment
           View Screenshot
           Review Order Details
                ↓
           Approve/Reject/Resubmit
                ↓
           Backend API
                ↓
           Update Payment Status
           Update Order Status
           Log Audit Trail
           Create Notification
                ↓
           Customer → Notification Update
```

### 7.4 Order Fulfillment Flow

```
Sales/Admin → Order Management
                ↓
           Update Status (PACKING)
                ↓
           Backend API
                ↓
           Validate Transition
           Update Order Status
           Log Status History
           Create Notification
                ↓
           Repeat for DISPATCHED → DELIVERED
```

---

## 8. Scalability Considerations

### 8.1 Current Design (Single Server)

- Designed for baseline: 200 orders/day
- Single PostgreSQL instance
- Single FastAPI instance
- MinIO for file storage
- Suitable for MVP and early growth

### 8.2 Future Scalability Options

**Database:**
- Read replicas for reporting queries
- Connection pooling optimization
- Query optimization and indexing

**Application:**
- Horizontal scaling of FastAPI instances (behind load balancer)
- Background job queue (Celery/RQ) for async tasks
- Caching layer (Redis) for product catalog

**Storage:**
- External S3 for production
- CDN for product images
- Image optimization pipeline

**Frontend:**
- CDN for static assets
- Service worker for offline capability (future)

---

## 9. Monitoring & Observability

### 9.1 Logging

- **Structured Logging:** JSON format logs
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Categories:**
  - Authentication events
  - Order creation/updates
  - Payment reviews
  - API errors
  - System events

### 9.2 Health Checks

- **Backend:** `/health` endpoint
  - Database connectivity check
  - Storage connectivity check
- **Frontend:** Health check endpoint (optional)
- **Docker:** Health check directives in compose

### 9.3 Metrics (Future)

- API response times
- Error rates
- Order processing times
- Payment review queue length
- Database query performance

---

## 10. Backup & Recovery

### 10.1 Database Backups

- **Strategy:** Daily automated backups
- **Method:** PostgreSQL pg_dump or continuous archiving
- **Storage:** External backup storage (separate from primary)
- **Retention:** Configurable (e.g., 30 days)

### 10.2 File Storage Backups

- **Strategy:** MinIO bucket replication or S3 versioning
- **Method:** Automated replication to secondary storage
- **Retention:** Configurable

### 10.3 Recovery Procedures

- Database restore from backup
- File storage restore from replica
- Point-in-time recovery (if configured)

---

## 11. Development Workflow

### 11.1 Local Development

1. Clone repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`
4. Run database migrations: `docker-compose exec backend alembic upgrade head`
5. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001

### 11.2 Database Migrations

- **Tool:** Alembic
- **Location:** Backend service migrations directory
- **Process:**
  - Create migration: `alembic revision --autogenerate -m "description"`
  - Apply migration: `alembic upgrade head`
  - Rollback: `alembic downgrade -1`

### 11.3 Testing Strategy (Future)

- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical flows

---

## 12. Future Architecture Considerations

### 12.1 Telegram Mini App Integration

- Same React frontend codebase
- Telegram WebApp wrapper
- Backend already supports Telegram auth
- Feature flag for Mini App mode

### 12.2 Microservices Extraction (If Needed)

Current modular design allows future extraction:
- Auth service → standalone microservice
- Payment service → standalone microservice
- Notification service → standalone microservice

### 12.3 Additional Features

- Background job queue for async processing
- Real-time notifications via WebSocket/SSE
- Advanced reporting and analytics
- Multi-branch inventory support
- Courier integration APIs

---

## 13. Open Implementation Decisions

The following decisions are left for implementation phase (as per SRS Section 13):

1. **OTP Provider:** SMS gateway vs Telegram OTP vs WhatsApp OTP
2. **Stock Reservation:** On order placement vs on payment approval
3. **Email Login:** Magic link vs email OTP
4. **Storage:** MinIO (recommended) vs S3
5. **State Management:** Redux vs Context API vs Zustand
6. **API Versioning:** URL path vs header-based
7. **Real-time Updates:** WebSocket vs Server-Sent Events vs polling
8. **Background Jobs:** Celery vs RQ vs FastAPI background tasks

---

## 14. Compliance & Standards

### 14.1 API Standards

- OpenAPI 3.0 specification
- RESTful conventions
- HTTP status codes
- Error response format

### 14.2 Code Standards

- Python: PEP 8 style guide
- JavaScript/TypeScript: ESLint configuration
- Code formatting: Black (Python), Prettier (JS/TS)

### 14.3 Documentation Standards

- API documentation via OpenAPI/Swagger
- Code comments for complex logic
- README files for setup instructions
- Architecture decision records (future)

---

**Document Status:** Draft v1.0  
**Last Updated:** Based on SRS v1.0  
**Next Review:** After implementation decisions are made

