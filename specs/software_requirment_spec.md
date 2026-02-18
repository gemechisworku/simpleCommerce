Below is an updated solution direction (aligned with **no complex payment integrations**) and a **detailed SRS** suitable as a single source of truth for an engineering/coding agent.

---

### Core flow

1. Customer browses **available products** (stock-aware).
2. Customer places an order (delivery address + preferred delivery window).
3. After order placement, the system shows:

   * **Payment options** (bank accounts/mobile wallets) configured in admin
   * **Payable amount** (items + delivery fee)
   * **Expected delivery date/window**
4. Customer pays externally and uploads **payment screenshot**.
5. Sales/Admin user:

   * reviews screenshot + order details
   * approves payment (or rejects with reason)
   * updates status through fulfillment: Packed → Dispatched → Delivered.

### Access channels (now + later)

* **Web app (mobile-first)**: primary catalog + ordering + account.
* **Telegram Mini App** (later): same backend, Telegram WebApp frontend wrapper.
* **Authentication**:

  * Telegram login (required when Mini App is used; optional on web)
  * Phone number OTP as primary login
  * Email as backup login + recovery
  * A single user identity can link: phone + email + telegram_id.

---

# Software Requirements Specification (SRS)

**Project Name:** Melegna Foods Commerce & Order Operations Platform
**Version:** 1.0
**Tech Environment:** Dockerized microservice-ish monolith (ReactJS + FastAPI + PostgreSQL)

---

## 1. Purpose and Scope

### 1.1 Purpose

Build a centralized platform to manage:

* Product catalog and availability
* Order placement from customers
* Manual-payment workflow using screenshots (no payment gateway integrations)
* Sales/admin approval of payments and operational status tracking
* Customer authentication via phone/email now; Telegram authentication for Mini App later

### 1.2 Scope

**In scope:**

* Web customer storefront (mobile-first)
* Admin dashboard for products, payments, orders, users, content, reporting
* Manual payment workflow: show payment methods, upload screenshot, approve/reject
* Status tracking and notifications (in-app; optional Telegram later)

**Out of scope (v1):**

* Direct payment gateway integrations (Stripe, etc.)
* Courier partner API integrations (optional in future)
* Automated bank reconciliation

---

## 2. Definitions

* **Customer:** end user buying products.
* **Sales User:** internal staff verifying payments and updating order statuses.
* **Admin:** full permissions, system configuration.
* **Telegram Mini App:** Telegram WebApp that loads the same frontend with Telegram auth context.

---

## 3. User Roles and Permissions

### 3.1 Roles

1. **Customer**

   * Browse products, place orders, upload payment proof, track orders
2. **Sales**

   * View all orders, verify payments, approve/reject, update fulfillment statuses
3. **Admin**

   * Everything Sales can do + manage products, inventory, payment options, pricing rules, users, roles, reporting, configuration

### 3.2 Permission Model (RBAC)

* JWT-based auth + role claims
* Admin can assign roles
* Optional fine-grained permissions (future): `orders:approve`, `products:write`, etc.

---

## 4. System Overview

### 4.1 High-level architecture

* **Frontend:** ReactJS (SPA) + responsive UI
* **Backend:** FastAPI (REST) + background jobs (Celery/RQ optional)
* **Database:** PostgreSQL
* **Storage:** Object storage for screenshots (S3-compatible like MinIO in Docker; or local volume for dev)
* **Deployment:** Docker Compose for dev and single-server deployment

### 4.2 Components

1. Customer Storefront
2. Admin Dashboard
3. Order & Payment Workflow Engine
4. Auth Service (phone OTP + email backup + Telegram auth link)
5. File Upload Service (payment screenshots)
6. Notification Layer (in-app + optional Telegram later)

---

## 5. Functional Requirements

### 5.1 Authentication and User Management

#### FR-AUTH-1 Phone OTP login (primary)

* Users authenticate with phone number via OTP.
* OTP delivery:

  * In v1, support pluggable providers (e.g., SMS gateway later); allow “dev mode OTP” in non-prod.
* After OTP verification, issue JWT access + refresh tokens.

#### FR-AUTH-2 Email backup login

* Users can login via email + OTP link/code OR passwordless magic link (choose one approach in implementation).
* Email is also used for recovery if phone inaccessible.

#### FR-AUTH-3 Telegram authentication (for Mini App + optional web)

* System must support linking a user account to a Telegram identity:

  * store `telegram_user_id`, `telegram_username`, `first_name`, `last_name`
* For Telegram Mini App:

  * verify Telegram initData signature server-side (Telegram WebApp auth validation)
  * if Telegram user not linked, prompt to link with phone OTP (one-time)

#### FR-AUTH-4 Account linking rules

* One internal user can have:

  * `phone` (unique, verified)
  * `email` (unique, verified)
  * `telegram_user_id` (unique, verified)
* Linking flow:

  * If Telegram login occurs and no match found:

    * create “telegram-only session” and require phone verification before ordering OR allow browsing only (configurable).
* Admin can merge accounts manually (future; optional).

#### FR-AUTH-5 Roles

* Admin assigns `customer`, `sales`, `admin`.
* Sales/Admin accounts created by Admin.

---

### 5.2 Product Catalog

#### FR-PROD-1 Product management (Admin)

* Create/edit/delete products
* Fields:

  * name, description, category, tags
  * base price
  * variants (size/weight/package) with independent price adjustments
  * images (multiple)
  * SKU (optional)
  * is_active, is_featured
  * availability settings (in_stock qty or “available/unavailable”)
* Soft delete recommended.

#### FR-PROD-2 Inventory

* Maintain stock quantity per product variant (or per product if no variants).
* Configurable behavior:

  * Reserve stock on order placement (recommended) OR on payment approval (alternative).
* Must prevent ordering more than available stock.

#### FR-PROD-3 Customer browsing

* List products, filter by category, search by name/tag
* Product detail page with variant selection, pricing, availability

---

### 5.3 Ordering

#### FR-ORD-1 Cart and checkout

* Customer can add items to cart with variant + quantity
* Checkout requires:

  * delivery address
  * recipient name
  * phone (auto from account but editable)
  * delivery instructions (optional)
* Delivery fee calculation:

  * based on zone/city/subcity (admin-managed rules)
* Place order creates an **Order** in status `PENDING_PAYMENT`.

#### FR-ORD-2 Post-order payment instruction view

After order creation, the system displays:

* Order number
* Total amount (items + delivery)
* Expected delivery window (calculated)
* Payment methods available (admin-managed list)
* Instructions for screenshot upload

#### FR-ORD-3 Order tracking

Customer sees:

* order timeline/status
* payment status (pending/approved/rejected)
* delivery status updates

#### FR-ORD-4 Order cancellation

* Customer can cancel order only if:

  * status is `PENDING_PAYMENT` AND no payment submitted OR payment not approved
* Sales/Admin can cancel anytime with reason and optional restocking.

---

### 5.4 Manual Payment Workflow (Screenshot-based)

#### FR-PAY-1 Payment methods management (Admin)

Admin can manage multiple payment options:

* Payment method type: Bank Transfer, Mobile Money, Other
* Display fields:

  * method name (e.g., “CBE Bank”, “Telebirr”, “Bank of Abyssinia”)
  * account number / wallet id
  * account holder name
  * instructions (text)
  * is_active
  * priority/order in list

#### FR-PAY-2 Payment submission by customer

Customer uploads:

* screenshot image (jpg/png)
* optional fields:

  * paid amount
  * transaction reference text
  * paid date/time (optional)
* After submission, order becomes `PAYMENT_SUBMITTED`.

#### FR-PAY-3 Payment review queue (Sales/Admin)

Sales dashboard shows orders with:

* payment submitted but not verified
* filters: date, amount, method, customer, order status
  Sales can:
* Approve payment -> order moves to `PAID` and triggers fulfillment flow
* Reject payment -> order moves to `PAYMENT_REJECTED` with reason visible to customer
* Request resubmission -> order moves to `PAYMENT_RESUBMIT_REQUESTED` (customer allowed to upload again)

#### FR-PAY-4 Audit trail

Any payment decision must be logged:

* who approved/rejected
* timestamp
* reason/notes
* previous status → new status

---

### 5.5 Fulfillment and Delivery Status

#### FR-FUL-1 Status model

Order lifecycle statuses (minimum):

* `PENDING_PAYMENT`
* `PAYMENT_SUBMITTED`
* `PAYMENT_RESUBMIT_REQUESTED`
* `PAYMENT_REJECTED`
* `PAID`
* `PACKING`
* `DISPATCHED`
* `DELIVERED`
* `CANCELLED`

#### FR-FUL-2 Sales/Admin updates

Sales/Admin can transition orders forward.
Invalid transitions must be blocked (config-driven state machine).

#### FR-FUL-3 Delivery ETA rules

Admin-configurable delivery windows by zone:

* Example: Addis Zone A = 1–2 days, Zone B = 2–3 days
* System calculates expected delivery date range on order placement.

#### FR-FUL-4 Proof of delivery (optional v1, recommended)

* Sales can mark delivered with:

  * delivery timestamp
  * optional note
  * optional delivery proof image

---

### 5.6 Notifications

#### FR-NOTIF-1 In-app notifications

* Customer: payment approved/rejected, status updates, delivery updates
* Sales/Admin: new order, new payment submitted

#### FR-NOTIF-2 Telegram notifications (future-ready)

* If Telegram linked, allow sending order status updates via Telegram bot (later).
* Must be behind feature flag.

---

### 5.7 Admin Dashboard

#### FR-ADM-1 Dashboard pages

* Orders (list + detail + status updates)
* Payments (review queue)
* Products + Categories
* Inventory
* Payment Methods
* Delivery Zones + Fees + ETAs
* Users + Roles
* Reporting

#### FR-ADM-2 Reporting (v1 minimum)

* Orders per day/week/month
* Revenue (approved payments) over time
* Top selling products
* Unpaid orders aging report
* Delivery completion rate

---

## 6. Data Requirements (Entities)

### 6.1 Core tables (PostgreSQL)

**users**

* id (UUID)
* phone, phone_verified
* email, email_verified
* telegram_user_id, telegram_username
* name fields
* role (enum: customer/sales/admin)
* created_at, updated_at

**products**

* id, name, description, category_id
* is_active, is_featured
* created_at, updated_at

**product_variants**

* id, product_id
* label (e.g., “250g”, “1kg pack”)
* price
* stock_qty
* sku (optional)
* is_active

**product_images**

* id, product_id, url, sort_order

**orders**

* id, order_number
* user_id
* status
* subtotal, delivery_fee, total
* delivery_zone_id
* delivery_address fields
* expected_delivery_from, expected_delivery_to
* created_at, updated_at

**order_items**

* id, order_id, product_id, variant_id
* qty, unit_price, line_total

**payment_methods**

* id, type, name
* account_identifier, account_holder
* instructions
* is_active, sort_order

**payments**

* id, order_id, method_id
* submitted_by_user_id
* amount_declared (nullable)
* reference_text (nullable)
* screenshot_url
* status (submitted/approved/rejected/resubmit_requested)
* reviewed_by, reviewed_at, review_note
* created_at

**order_status_history**

* id, order_id
* old_status, new_status
* actor_user_id
* note
* created_at

**delivery_zones**

* id, name
* fee
* eta_min_days, eta_max_days
* is_active

---

## 7. API Requirements (FastAPI)

### 7.1 Auth

* `POST /auth/otp/request` (phone)
* `POST /auth/otp/verify`
* `POST /auth/email/request` (magic link/OTP)
* `POST /auth/email/verify`
* `POST /auth/telegram/verify` (validate initData, link account)
* `POST /auth/refresh`
* `POST /auth/logout`

### 7.2 Customer

* `GET /products`
* `GET /products/{id}`
* `POST /cart/checkout` -> creates order
* `GET /orders/my`
* `GET /orders/{id}` (customer-owned)
* `POST /orders/{id}/payment` (upload screenshot + meta)
* `POST /orders/{id}/cancel`

### 7.3 Admin/Sales

* `GET /admin/orders`
* `GET /admin/orders/{id}`
* `POST /admin/orders/{id}/status`
* `GET /admin/payments/queue`
* `POST /admin/payments/{id}/approve`
* `POST /admin/payments/{id}/reject`
* `POST /admin/payments/{id}/resubmit_request`

### 7.4 Admin configuration

* CRUD for products, variants, inventory, categories
* CRUD for payment methods
* CRUD for delivery zones

---

## 8. Non-Functional Requirements

### 8.1 Performance

* Product list page should load in < 2 seconds on 3G-like conditions (mobile-first caching + pagination)
* Support at least:

  * 1,000 products (future)
  * 200 orders/day without degradation (single server baseline)

### 8.2 Security

* All endpoints require HTTPS in production
* JWT access tokens short-lived + refresh tokens
* RBAC enforced server-side
* Uploaded screenshots scanned/validated by type + size limits
* Rate limit OTP requests per phone/IP
* Telegram initData signature validation required

### 8.3 Reliability

* Database backups (daily)
* Upload storage redundancy (MinIO or external S3)
* Idempotent order creation to avoid duplicate on retries

### 8.4 Auditability

* All status transitions logged in `order_status_history`
* All payment reviews logged in `payments`

### 8.5 Maintainability

* Docker-based local dev
* Structured logging (JSON logs)
* API docs via OpenAPI/Swagger
* Migrations with Alembic

---

## 9. UX Requirements

### 9.1 Customer UX

* Very few steps: Browse → Order → Pay instructions → Upload screenshot → Track status
* Payment instructions page must be clear and copyable (account numbers + names)
* Order status timeline visible

### 9.2 Sales/Admin UX

* Payment review queue optimized for speed:

  * view screenshot inline
  * approve/reject in one click with optional note
* Orders board with filters by status

---

## 10. Docker & DevOps Requirements

### 10.1 Docker services (docker-compose)

* `frontend` (React)
* `backend` (FastAPI + Uvicorn)
* `db` (Postgres)
* `storage` (MinIO) + `minio-init` (optional)
* `nginx` (reverse proxy) in production compose

### 10.2 Environments

* `.env` for secrets and config:

  * DB URL, JWT secret, OTP provider keys, storage keys, Telegram bot/app keys
* Separate compose overrides: `docker-compose.dev.yml`, `docker-compose.prod.yml`

---

## 11. Acceptance Criteria (MVP)

1. Customer can:

   * sign up/login with phone OTP
   * browse products
   * place order for in-stock items
   * see payment methods after ordering
   * upload payment screenshot
   * track order status

2. Admin can:

   * manage products and stock
   * configure multiple payment methods
   * configure delivery zones/fees/ETAs

3. Sales can:

   * see payment submission queue
   * approve/reject/resubmit request
   * update order statuses through delivery

4. Telegram readiness:

   * backend supports linking telegram_user_id and validating Telegram initData (even if Mini App UI is later)

---

## 12. Future Enhancements (explicitly planned)

* Telegram Mini App UI packaging (same React app in Telegram WebApp mode)
* Telegram bot notifications
* Customer reorder in 1 click
* Discount codes / bundles
* Multi-branch inventory
* Courier assignment + tracking
* Basic accounting export (CSV)

---

## 13. Open Implementation Choices (engineering decisions)

These are intentionally left as “choose one” but should be decided during build:

* OTP provider (SMS gateway vs Telegram OTP vs WhatsApp OTP)
* Stock reservation timing: on order placement vs on payment approval
* Email login: magic link vs email OTP
* Storage: MinIO vs S3 (MinIO recommended in Docker)

