# Project Meta & Architectural Principles

**Project Name:** simpleCommerce Commerce & Order Operations Platform  
**Version:** 1.0  
**Last Updated:** Based on all specification documents v1.0

---

## 1. Project Overview

### 1.1 Purpose

A centralized e-commerce platform for managing product catalogs, customer orders, and manual payment workflows with screenshot-based payment verification.

### 1.2 Core Architecture Pattern

**Microservice-ish Monolith:**
- Single codebase with modular components
- Monolithic deployment for simplicity (single-server baseline)
- Clear separation of concerns through logical modules
- Designed to support future service extraction if needed

### 1.3 Technology Stack

- **Frontend:** ReactJS (SPA), Mobile-first responsive design
- **Backend:** FastAPI (Python) with Uvicorn
- **Database:** PostgreSQL with SQLAlchemy + Alembic
- **Storage:** MinIO (S3-compatible) for file storage
- **Infrastructure:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (production)

---

## 2. Core Architectural Principles

### 2.1 Separation of Concerns

- **Modular Components:** Clear boundaries between Customer Storefront, Admin Dashboard, Auth Service, Order Engine, File Upload Service, and Notification Layer
- **Service Boundaries:** Each component has well-defined responsibilities and interfaces
- **Layered Architecture:** Client Layer → Reverse Proxy → Application Layer → Data Layer

### 2.2 API-First Design

- **RESTful APIs:** All functionality exposed via REST endpoints
- **API Versioning:** URL path versioning (`/api/v1/`)
- **OpenAPI Documentation:** All APIs documented via Swagger/OpenAPI
- **Stateless:** Each request contains all necessary information
- **Standardized Responses:** Consistent response format across all endpoints

### 2.3 Database Design Principles

- **Relational Model:** Normalized relational database design
- **Data Integrity:** Foreign keys, check constraints, and unique constraints enforced at database level
- **Audit Trail:** Timestamps and history tables for critical operations (order status changes, payment reviews)
- **Soft Deletes:** Use flags (`is_active`, `deleted_at`) for logical deletion where appropriate
- **Primary Key Strategy:** UUID for security-sensitive entities (users), BIGSERIAL for high-volume entities (orders, products)
- **Naming Conventions:** `snake_case` for tables and columns, consistent patterns

### 2.4 Security-First Approach

- **Authentication:** JWT-based with short-lived access tokens (15 min) and longer-lived refresh tokens (7 days)
- **Authorization:** Role-Based Access Control (RBAC) enforced server-side on every request
- **Input Validation:** All inputs validated using Pydantic models (backend) and form validation (frontend)
- **SQL Injection Prevention:** ORM parameterized queries only, no raw SQL
- **XSS Prevention:** Input sanitization and Content Security Policy headers
- **File Upload Security:** Type validation, size limits, secure storage
- **Rate Limiting:** Applied to OTP requests, API endpoints, and file uploads
- **HTTPS:** All production traffic over HTTPS with SSL/TLS

### 2.5 State Management

- **Order Status State Machine:** Config-driven state machine with enforced valid transitions
- **Payment Status Transitions:** Controlled workflow with audit trail
- **Stock Reservation:** Configurable strategy (on order placement or payment approval)
- **Idempotent Operations:** Order creation and critical operations are idempotent

### 2.6 Error Handling

- **Standardized Error Responses:** Consistent error format across all APIs
- **Business Rule Validation:** Server-side validation of all business rules
- **Graceful Degradation:** System continues to function when non-critical components fail
- **User-Friendly Messages:** Clear, actionable error messages for users

### 2.7 Performance Principles

- **Mobile-First:** Optimized for mobile devices and slower connections
- **Pagination:** All list endpoints support pagination
- **Caching Strategy:** Product catalog caching (future)
- **Lazy Loading:** Images and non-critical content loaded on demand
- **Query Optimization:** Appropriate indexes, avoid N+1 queries
- **Connection Pooling:** Database connection pooling configured

### 2.8 Scalability Considerations

- **Current Baseline:** Designed for 200 orders/day on single server
- **Future-Ready:** Architecture supports horizontal scaling when needed
- **Database Optimization:** Indexes optimized for common query patterns
- **Stateless Services:** Backend services are stateless, enabling horizontal scaling

### 2.9 Maintainability

- **Code Organization:** Modular structure with clear separation
- **Documentation:** API docs, code comments, README files
- **Database Migrations:** Alembic for version-controlled schema changes
- **Structured Logging:** JSON format logs for easy parsing
- **Environment Configuration:** `.env` files with compose overrides

### 2.10 Observability

- **Health Checks:** `/health` endpoint for monitoring
- **Structured Logging:** JSON logs with appropriate log levels
- **Audit Trail:** All critical operations logged (order status changes, payment reviews)
- **Error Tracking:** Errors logged with context for debugging

---

## 3. Frontend Architecture Principles

### 3.1 Component Architecture

- **Atomic Design:** Components organized as atoms, molecules, organisms, templates, pages
- **Reusability:** Shared component library for consistency
- **Composition:** Build complex UIs from simple, reusable components
- **Single Responsibility:** Each component has one clear purpose

### 3.2 State Management

- **Client-Side State:** Shopping cart, UI state managed client-side
- **Server State:** Product data, orders, user data fetched from API
- **State Synchronization:** Keep client and server state in sync
- **Optimistic Updates:** Update UI optimistically where appropriate

### 3.3 Routing

- **SPA Routing:** Client-side routing for seamless navigation
- **Protected Routes:** Authentication and role-based route protection
- **Deep Linking:** All pages accessible via direct URLs
- **History Management:** Browser history properly managed

### 3.4 Responsive Design

- **Mobile-First:** Design for mobile, enhance for desktop
- **Breakpoints:** Mobile (< 768px), Tablet (768px - 1024px), Desktop (> 1024px)
- **Touch-Friendly:** Minimum 44x44px touch targets
- **Progressive Enhancement:** Core functionality works on all devices

### 3.5 Accessibility

- **WCAG 2.1 AA Compliance:** Meet accessibility standards
- **Keyboard Navigation:** All interactive elements keyboard accessible
- **Screen Reader Support:** Semantic HTML, ARIA labels
- **Color Contrast:** Sufficient contrast ratios
- **Focus Management:** Visible focus indicators

---

## 4. Backend Architecture Principles

### 4.1 API Design

- **RESTful Conventions:** Follow REST principles
- **Resource-Based URLs:** Clear, hierarchical URL structure
- **HTTP Methods:** Proper use of GET, POST, PUT, PATCH, DELETE
- **Status Codes:** Appropriate HTTP status codes
- **Request/Response Validation:** Pydantic models for validation

### 4.2 Service Layer Organization

- **Service Modules:** Auth Service, Product Catalog Service, Order Engine, File Upload Service, Notification Layer, Admin Service
- **Dependency Injection:** Use dependency injection for testability
- **Business Logic:** Business rules in service layer, not in controllers
- **Data Access Layer:** ORM models and repositories separate from business logic

### 4.3 Error Handling

- **Exception Handling:** Consistent exception handling strategy
- **Error Responses:** Standardized error response format
- **Logging:** Errors logged with full context
- **User-Friendly Messages:** Transform technical errors to user-friendly messages

### 4.4 Database Access

- **ORM Usage:** SQLAlchemy ORM for all database access
- **Migrations:** Alembic for schema versioning
- **Transactions:** Proper transaction management
- **Connection Management:** Connection pooling and proper cleanup

---

## 5. Global Theme System

### 5.1 Theme Configuration

The application must support a **global theme configuration system** that allows developers to customize the visual appearance of the entire application through a centralized theme configuration.

### 5.2 Theme Properties

**Color Palette:**
- **Primary Color:** Main brand color used for primary actions, links, and key UI elements
- **Secondary Color:** Supporting brand color for secondary actions and accents
- **Highlighting Color:** Color for highlighting important information, success states, and emphasis
- **Background Colors:** 
  - Primary background
  - Secondary background
  - Surface/panel background
- **Text Colors:**
  - Primary text
  - Secondary text
  - Muted/disabled text
- **Status Colors:**
  - Success (green)
  - Error (red)
  - Warning (yellow/orange)
  - Info (blue)
- **Border Colors:**
  - Default border
  - Focus border
  - Error border

**Typography:**
- **Font Families:**
  - Primary font family (body text)
  - Secondary font family (headings, optional)
  - Monospace font family (code, optional)
- **Font Sizes:** Typography scale (e.g., xs, sm, base, lg, xl, 2xl, 3xl, etc.)
- **Font Weights:** Available weights (light, normal, medium, semibold, bold)
- **Line Heights:** Line height scale
- **Letter Spacing:** Letter spacing values

**Spacing:**
- **Spacing Scale:** Consistent spacing scale (e.g., 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px)
- **Component Spacing:** Padding and margin values for components

**Border Radius:**
- **Border Radius Scale:** Consistent border radius values (e.g., none, sm, md, lg, xl, full)

**Shadows:**
- **Shadow Scale:** Elevation shadows for depth (e.g., sm, md, lg, xl)

**Breakpoints:**
- **Responsive Breakpoints:** Mobile, tablet, desktop breakpoint values

**Transitions:**
- **Animation Durations:** Standard transition durations
- **Easing Functions:** Easing curves for animations

### 5.3 Theme Implementation

**Configuration File:**
- Theme configuration should be in a centralized location (e.g., `theme.config.js` or `theme.ts`)
- Should export a theme object with all properties
- Should support TypeScript types for type safety

**Usage Pattern:**
```typescript
// Example theme structure
const theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    highlight: '#ffc107',
    // ... other colors
  },
  typography: {
    fontFamily: {
      primary: 'Inter, sans-serif',
      secondary: 'Roboto, sans-serif',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      // ... other sizes
    },
    // ... other typography properties
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    // ... other spacing values
  },
  // ... other theme properties
}
```

**Component Integration:**
- All components should use theme values instead of hardcoded colors/sizes
- Theme should be accessible throughout the component tree (Context API, theme provider)
- CSS-in-JS or CSS variables approach for theme application

**Theme Provider:**
- React Context or theme provider to make theme available to all components
- Support for theme switching (light/dark mode) in future

**Default Theme:**
- Provide sensible defaults for all theme properties
- Ensure accessibility standards are met with default colors

---

## 6. Code Standards

### 6.1 Naming Conventions

**Frontend (JavaScript/TypeScript):**
- **Components:** PascalCase (e.g., `ProductCard`, `OrderList`)
- **Files:** Match component name or kebab-case for utilities
- **Variables/Functions:** camelCase (e.g., `getUserOrders`, `orderStatus`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `API_BASE_URL`, `MAX_FILE_SIZE`)
- **CSS Classes:** kebab-case (e.g., `product-card`, `order-list-item`)

**Backend (Python):**
- **Modules/Packages:** snake_case (e.g., `order_service.py`, `auth_service.py`)
- **Classes:** PascalCase (e.g., `OrderService`, `UserModel`)
- **Functions/Variables:** snake_case (e.g., `create_order`, `user_id`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `MAX_OTP_ATTEMPTS`, `DEFAULT_PAGE_SIZE`)

**Database:**
- **Tables:** snake_case, plural (e.g., `users`, `order_items`)
- **Columns:** snake_case (e.g., `user_id`, `created_at`)
- **Primary Keys:** `id`
- **Foreign Keys:** `{referenced_table}_id`

### 6.2 Code Organization

**Frontend:**
```
src/
  components/     # Reusable components
  pages/          # Page components
  services/       # API services
  hooks/          # Custom React hooks
  utils/          # Utility functions
  types/          # TypeScript types
  theme/          # Theme configuration
  constants/      # Constants
```

**Backend:**
```
app/
  api/            # API routes
  services/       # Business logic
  models/         # Database models
  schemas/        # Pydantic schemas
  utils/          # Utility functions
  core/           # Core configuration
  migrations/     # Alembic migrations
```

### 6.3 Code Quality

- **Type Safety:** TypeScript for frontend, type hints for Python
- **Linting:** ESLint (frontend), Flake8/Black (backend)
- **Formatting:** Prettier (frontend), Black (backend)
- **Testing:** Unit tests, integration tests (future)
- **Documentation:** Code comments for complex logic

---

## 7. Security Principles

### 7.1 Authentication

- **JWT Tokens:** Short-lived access tokens, longer-lived refresh tokens
- **Token Storage:** HTTP-only cookies (recommended) or secure storage
- **Token Rotation:** Optional refresh token rotation
- **Multi-Identity:** Support phone, email, Telegram authentication

### 7.2 Authorization

- **RBAC:** Role-based access control (customer, sales, admin)
- **Server-Side Enforcement:** All authorization checks on server
- **Resource Ownership:** Customers can only access their own resources
- **State Machine:** Invalid state transitions blocked

### 7.3 Data Protection

- **Input Validation:** Validate all inputs (client and server)
- **SQL Injection Prevention:** ORM only, parameterized queries
- **XSS Prevention:** Input sanitization, CSP headers
- **CSRF Protection:** CSRF tokens for state-changing operations
- **Sensitive Data:** Encrypt sensitive data at rest (if required)

### 7.4 File Security

- **File Validation:** Type and size validation
- **Secure Storage:** Files stored outside web root
- **Access Control:** Authenticated access to uploaded files
- **Virus Scanning:** Optional virus scanning (future)

---

## 8. Performance Principles

### 8.1 Frontend Performance

- **Code Splitting:** Lazy load routes and components
- **Image Optimization:** Optimize images, lazy loading
- **Bundle Size:** Minimize bundle size, tree shaking
- **Caching:** Browser caching for static assets
- **Service Worker:** Optional PWA features (future)

### 8.2 Backend Performance

- **Database Indexing:** Appropriate indexes for queries
- **Query Optimization:** Avoid N+1 queries, use eager loading
- **Connection Pooling:** Database connection pooling
- **Caching:** Cache frequently accessed data (future)
- **Pagination:** All list endpoints paginated

### 8.3 Network Performance

- **API Optimization:** Minimize API calls, batch requests where possible
- **Compression:** Gzip/Brotli compression
- **CDN:** Use CDN for static assets (future)

---

## 9. Development Workflow

### 9.1 Local Development

- **Docker Compose:** All services run via Docker Compose
- **Hot Reload:** Frontend and backend hot reload in development
- **Environment Variables:** `.env` files for configuration
- **Database Migrations:** Alembic migrations for schema changes

### 9.2 Version Control

- **Git Workflow:** Feature branches, pull requests
- **Commit Messages:** Clear, descriptive commit messages
- **Code Review:** All code reviewed before merge

### 9.3 Testing

- **Unit Tests:** Test individual components and functions
- **Integration Tests:** Test API endpoints and workflows
- **E2E Tests:** Test critical user flows (future)

---

## 10. Deployment Principles

### 10.1 Environment Configuration

- **Environment Variables:** All configuration via environment variables
- **Secrets Management:** Secrets not committed to repository
- **Environment Separation:** Dev, staging, production environments

### 10.2 Docker Strategy

- **Multi-Stage Builds:** Optimize Docker image sizes
- **Health Checks:** Health check endpoints for containers
- **Volume Management:** Persistent volumes for database and storage

### 10.3 Monitoring

- **Health Checks:** Application health monitoring
- **Logging:** Structured logging for debugging
- **Error Tracking:** Error monitoring and alerting (future)

---

## 11. Future Considerations

### 11.1 Scalability

- **Horizontal Scaling:** Architecture supports scaling out
- **Read Replicas:** Database read replicas for reporting
- **Caching Layer:** Redis for caching (future)
- **Background Jobs:** Celery/RQ for async tasks (future)

### 11.2 Feature Enhancements

- **Telegram Mini App:** Same React app in Telegram WebApp wrapper
- **Real-Time Updates:** WebSocket/SSE for notifications
- **Advanced Reporting:** Enhanced analytics and reporting
- **Multi-Branch:** Support for multiple branches/locations

---

## 12. Compliance and Standards

### 12.1 API Standards

- **OpenAPI 3.0:** API specification format
- **RESTful Conventions:** Follow REST best practices
- **HTTP Status Codes:** Proper use of status codes
- **Error Format:** Standardized error response format

### 12.2 Code Standards

- **Python:** PEP 8 style guide
- **JavaScript/TypeScript:** ESLint configuration, Prettier formatting
- **SQL:** Consistent formatting and naming

### 12.3 Documentation Standards

- **API Documentation:** OpenAPI/Swagger
- **Code Comments:** Comments for complex logic
- **README Files:** Setup and usage instructions
- **Architecture Decision Records:** Document major decisions (future)

---

**Document Status:** Draft v1.0  
**Last Updated:** Based on all specification documents v1.0  
**Next Review:** As architecture evolves

