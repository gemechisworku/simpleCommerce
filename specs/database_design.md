# Database Design Document

**Project Name:** Melegna Foods Commerce & Order Operations Platform  
**Version:** 1.0  
**Database:** PostgreSQL  
**Based on:** Software Requirements Specification v1.0 & Architecture Design v1.0

---

## 1. Database Overview

### 1.1 Design Principles

- **Relational Model:** Normalized relational database design
- **Data Integrity:** Foreign keys, check constraints, and unique constraints
- **Audit Trail:** Timestamps and history tables for critical operations
- **Soft Deletes:** Use flags for logical deletion where appropriate
- **UUID Primary Keys:** For security-sensitive entities (users)
- **Sequential IDs:** For high-volume entities (orders, products)
- **Multi-Identity Support:** Users can have phone, email, and Telegram ID (all unique when present)

### 1.2 Database Naming Conventions

- **Tables:** `snake_case`, plural (e.g., `users`, `order_items`)
- **Columns:** `snake_case` (e.g., `user_id`, `created_at`)
- **Primary Keys:** `id`
- **Foreign Keys:** `{referenced_table}_id` (e.g., `user_id`, `product_id`)
- **Timestamps:** `created_at`, `updated_at`
- **Boolean Flags:** `is_{attribute}` (e.g., `is_active`, `is_verified`)
- **Enums:** PostgreSQL ENUM types with uppercase values

---

## 2. Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (UUID) PK    │
│ phone           │◄──────┐
│ email           │       │
│ telegram_id     │       │
│ role            │       │
└────────┬────────┘       │
         │                │
         │ 1               │
         │                 │
         │ N               │
    ┌────▼────────────┐    │
    │    orders       │    │
    │─────────────────│    │
    │ id (BIGINT) PK  │    │
    │ user_id FK      │────┘
    │ order_number    │
    │ status          │
    │ delivery_zone_id│──┐
    └────┬────────────┘  │
         │               │
         │ 1              │
         │                │
         │ N              │
    ┌────▼────────────┐   │
    │  order_items    │   │
    │─────────────────│   │
    │ id (BIGINT) PK  │   │
    │ order_id FK     │───┘
    │ product_id FK   │──┐
    │ variant_id FK   │──┤
    └─────────────────┘  │
                         │
┌─────────────────┐      │
│   products      │      │
│─────────────────│      │
│ id (BIGINT) PK  │◄─────┘
│ category_id FK  │──┐
│ name            │  │
│ is_active       │  │
└────┬────────────┘  │
     │                │
     │ 1              │
     │                │
     │ N              │
┌────▼────────────┐   │
│product_variants │   │
│─────────────────│   │
│ id (BIGINT) PK  │   │
│ product_id FK   │───┘
│ stock_qty       │
└─────────────────┘

┌─────────────────┐
│  delivery_zones │
│─────────────────│
│ id (BIGINT) PK  │◄──────┐
│ name            │       │
│ fee             │       │
└─────────────────┘       │
                          │
┌─────────────────┐       │
│ payment_methods │       │
│─────────────────│       │
│ id (BIGINT) PK  │       │
│ type            │       │
│ is_active       │       │
└────┬────────────┘       │
     │                    │
     │ 1                  │
     │                    │
     │ N                  │
┌────▼────────────┐       │
│    payments      │       │
│─────────────────│       │
│ id (BIGINT) PK  │       │
│ order_id FK     │───────┼──┐
│ method_id FK    │───┐   │  │
│ status          │   │   │  │
│ reviewed_by FK  │───┼───┼──┘
└─────────────────┘   │   │
                      │   │
┌─────────────────┐   │   │
│order_status_    │   │   │
│history          │   │   │
│─────────────────│   │   │
│ id (BIGINT) PK  │   │   │
│ order_id FK     │───┼───┘
│ actor_user_id FK│───┘
└─────────────────┘
```

---

## 3. Core Tables

### 3.1 users

User accounts with multi-identity support (phone, email, Telegram).

**Table:** `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| `phone` | VARCHAR(20) | UNIQUE, NULL allowed | Phone number (E.164 format recommended) |
| `phone_verified` | BOOLEAN | NOT NULL, DEFAULT false | Phone verification status |
| `email` | VARCHAR(255) | UNIQUE, NULL allowed | Email address |
| `email_verified` | BOOLEAN | NOT NULL, DEFAULT false | Email verification status |
| `telegram_user_id` | BIGINT | UNIQUE, NULL allowed | Telegram user ID |
| `telegram_username` | VARCHAR(100) | NULL allowed | Telegram username |
| `first_name` | VARCHAR(100) | NULL allowed | User's first name |
| `last_name` | VARCHAR(100) | NULL allowed | User's last name |
| `role` | user_role_enum | NOT NULL, DEFAULT 'customer' | User role (customer/sales/admin) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Account active status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_users_phone` ON `phone` WHERE `phone IS NOT NULL AND phone_verified = true` (partial unique index)
- `idx_users_email` ON `email` WHERE `email IS NOT NULL AND email_verified = true` (partial unique index)
- `idx_users_telegram_user_id` ON `telegram_user_id` WHERE `telegram_user_id IS NOT NULL` (partial unique index)
- `idx_users_role` ON `role`
- `idx_users_created_at` ON `created_at`

**Constraints:**
- At least one of `phone`, `email`, or `telegram_user_id` must be present (application-level check recommended)
- `phone` must be unique when `phone_verified = true`
- `email` must be unique when `email_verified = true`
- `telegram_user_id` must be unique when present

**Enum Type:**
```sql
CREATE TYPE user_role_enum AS ENUM ('customer', 'sales', 'admin');
```

---

### 3.2 categories

Product categories for organization.

**Table:** `categories`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Category identifier |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Category name |
| `slug` | VARCHAR(100) | NOT NULL, UNIQUE | URL-friendly identifier |
| `description` | TEXT | NULL allowed | Category description |
| `parent_id` | BIGINT | NULL allowed, FK to categories.id | Parent category for hierarchy |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Category active status |
| `sort_order` | INTEGER | NOT NULL, DEFAULT 0 | Display order |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_categories_slug` ON `slug`
- `idx_categories_parent_id` ON `parent_id`
- `idx_categories_is_active` ON `is_active`

**Foreign Keys:**
- `parent_id` REFERENCES `categories(id)` ON DELETE SET NULL

---

### 3.3 products

Product catalog entries.

**Table:** `products`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Product identifier |
| `name` | VARCHAR(200) | NOT NULL | Product name |
| `slug` | VARCHAR(200) | NOT NULL, UNIQUE | URL-friendly identifier |
| `description` | TEXT | NULL allowed | Product description |
| `category_id` | BIGINT | NULL allowed, FK to categories.id | Product category |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Product active status |
| `is_featured` | BOOLEAN | NOT NULL, DEFAULT false | Featured product flag |
| `deleted_at` | TIMESTAMP | NULL allowed | Soft delete timestamp |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_products_slug` ON `slug`
- `idx_products_category_id` ON `category_id`
- `idx_products_is_active` ON `is_active` WHERE `is_active = true AND deleted_at IS NULL`
- `idx_products_is_featured` ON `is_featured` WHERE `is_featured = true AND deleted_at IS NULL`
- `idx_products_deleted_at` ON `deleted_at` WHERE `deleted_at IS NULL` (partial index for active products)

**Foreign Keys:**
- `category_id` REFERENCES `categories(id)` ON DELETE SET NULL

**Notes:**
- Soft delete implemented via `deleted_at` timestamp
- Active products: `is_active = true AND deleted_at IS NULL`

---

### 3.4 product_variants

Product variants (size, weight, package) with independent pricing and stock.

**Table:** `product_variants`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Variant identifier |
| `product_id` | BIGINT | NOT NULL, FK to products.id | Parent product |
| `label` | VARCHAR(100) | NOT NULL | Variant label (e.g., "250g", "1kg pack") |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK (price >= 0) | Variant price |
| `stock_qty` | INTEGER | NOT NULL, DEFAULT 0, CHECK (stock_qty >= 0) | Available stock quantity |
| `sku` | VARCHAR(50) | NULL allowed, UNIQUE | Stock keeping unit |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Variant active status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_product_variants_product_id` ON `product_id`
- `idx_product_variants_sku` ON `sku` WHERE `sku IS NOT NULL`
- `idx_product_variants_is_active` ON `is_active` WHERE `is_active = true`

**Foreign Keys:**
- `product_id` REFERENCES `products(id)` ON DELETE CASCADE

**Unique Constraint:**
- `(product_id, label)` - Unique variant label per product

**Notes:**
- Stock quantity managed at variant level
- Price stored as DECIMAL for precision

---

### 3.5 product_images

Product images with sort order.

**Table:** `product_images`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Image identifier |
| `product_id` | BIGINT | NOT NULL, FK to products.id | Product reference |
| `url` | VARCHAR(500) | NOT NULL | Image URL (MinIO/S3) |
| `alt_text` | VARCHAR(200) | NULL allowed | Image alt text for accessibility |
| `sort_order` | INTEGER | NOT NULL, DEFAULT 0 | Display order |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_product_images_product_id` ON `product_id`
- `idx_product_images_sort_order` ON `(product_id, sort_order)`

**Foreign Keys:**
- `product_id` REFERENCES `products(id)` ON DELETE CASCADE

---

### 3.6 delivery_zones

Delivery zones with fees and ETAs.

**Table:** `delivery_zones`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Zone identifier |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Zone name |
| `description` | TEXT | NULL allowed | Zone description |
| `fee` | DECIMAL(10,2) | NOT NULL, CHECK (fee >= 0) | Delivery fee |
| `eta_min_days` | INTEGER | NOT NULL, DEFAULT 1, CHECK (eta_min_days >= 0) | Minimum delivery days |
| `eta_max_days` | INTEGER | NOT NULL, DEFAULT 2, CHECK (eta_max_days >= eta_min_days) | Maximum delivery days |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Zone active status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_delivery_zones_name` ON `name`
- `idx_delivery_zones_is_active` ON `is_active` WHERE `is_active = true`

**Constraints:**
- `eta_max_days >= eta_min_days`

---

### 3.7 orders

Order records with status and delivery information.

**Table:** `orders`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Order identifier |
| `order_number` | VARCHAR(20) | NOT NULL, UNIQUE | Human-readable order number |
| `user_id` | UUID | NOT NULL, FK to users.id | Customer who placed order |
| `status` | order_status_enum | NOT NULL, DEFAULT 'PENDING_PAYMENT' | Current order status |
| `subtotal` | DECIMAL(10,2) | NOT NULL, CHECK (subtotal >= 0) | Items subtotal |
| `delivery_fee` | DECIMAL(10,2) | NOT NULL, CHECK (delivery_fee >= 0) | Delivery fee |
| `total` | DECIMAL(10,2) | NOT NULL, CHECK (total >= 0) | Total amount (subtotal + delivery_fee) |
| `delivery_zone_id` | BIGINT | NULL allowed, FK to delivery_zones.id | Delivery zone |
| `delivery_address` | TEXT | NOT NULL | Full delivery address |
| `recipient_name` | VARCHAR(100) | NOT NULL | Recipient name |
| `recipient_phone` | VARCHAR(20) | NOT NULL | Recipient phone |
| `delivery_instructions` | TEXT | NULL allowed | Delivery instructions |
| `expected_delivery_from` | DATE | NULL allowed | Expected delivery start date |
| `expected_delivery_to` | DATE | NULL allowed | Expected delivery end date |
| `cancelled_at` | TIMESTAMP | NULL allowed | Cancellation timestamp |
| `cancellation_reason` | TEXT | NULL allowed | Cancellation reason |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Order creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_orders_order_number` ON `order_number` (unique)
- `idx_orders_user_id` ON `user_id`
- `idx_orders_status` ON `status`
- `idx_orders_created_at` ON `created_at`
- `idx_orders_delivery_zone_id` ON `delivery_zone_id`
- Composite index: `idx_orders_user_status` ON `(user_id, status)`
- Composite index: `idx_orders_status_created` ON `(status, created_at)`

**Foreign Keys:**
- `user_id` REFERENCES `users(id)` ON DELETE RESTRICT
- `delivery_zone_id` REFERENCES `delivery_zones(id)` ON DELETE SET NULL

**Constraints:**
- `total = subtotal + delivery_fee` (application-level validation)
- `expected_delivery_to >= expected_delivery_from` (when both present)

**Enum Type:**
```sql
CREATE TYPE order_status_enum AS ENUM (
    'PENDING_PAYMENT',
    'PAYMENT_SUBMITTED',
    'PAYMENT_RESUBMIT_REQUESTED',
    'PAYMENT_REJECTED',
    'PAID',
    'PACKING',
    'DISPATCHED',
    'DELIVERED',
    'CANCELLED'
);
```

**Order Number Generation:**
- Format: `ORD-{YYYYMMDD}-{sequential_number}`
- Example: `ORD-20240115-0001`
- Generated application-side with uniqueness check

---

### 3.8 order_items

Order line items with product and variant references.

**Table:** `order_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Order item identifier |
| `order_id` | BIGINT | NOT NULL, FK to orders.id | Parent order |
| `product_id` | BIGINT | NOT NULL, FK to products.id | Product reference |
| `variant_id` | BIGINT | NULL allowed, FK to product_variants.id | Variant reference (if applicable) |
| `product_name` | VARCHAR(200) | NOT NULL | Product name snapshot |
| `variant_label` | VARCHAR(100) | NULL allowed | Variant label snapshot |
| `quantity` | INTEGER | NOT NULL, CHECK (quantity > 0) | Ordered quantity |
| `unit_price` | DECIMAL(10,2) | NOT NULL, CHECK (unit_price >= 0) | Price per unit at time of order |
| `line_total` | DECIMAL(10,2) | NOT NULL, CHECK (line_total >= 0) | Line total (quantity * unit_price) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_order_items_order_id` ON `order_id`
- `idx_order_items_product_id` ON `product_id`
- `idx_order_items_variant_id` ON `variant_id`

**Foreign Keys:**
- `order_id` REFERENCES `orders(id)` ON DELETE CASCADE
- `product_id` REFERENCES `products(id)` ON DELETE RESTRICT
- `variant_id` REFERENCES `product_variants(id)` ON DELETE SET NULL

**Constraints:**
- `line_total = quantity * unit_price` (application-level validation)
- Product name and variant label stored as snapshots for historical accuracy

---

### 3.9 payment_methods

Admin-configured payment methods (bank accounts, mobile wallets).

**Table:** `payment_methods`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Payment method identifier |
| `type` | payment_method_type_enum | NOT NULL | Payment method type |
| `name` | VARCHAR(100) | NOT NULL | Display name (e.g., "CBE Bank", "Telebirr") |
| `account_identifier` | VARCHAR(100) | NOT NULL | Account number or wallet ID |
| `account_holder` | VARCHAR(100) | NOT NULL | Account holder name |
| `instructions` | TEXT | NULL allowed | Payment instructions |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Method active status |
| `sort_order` | INTEGER | NOT NULL, DEFAULT 0 | Display order |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_payment_methods_type` ON `type`
- `idx_payment_methods_is_active` ON `is_active` WHERE `is_active = true`
- `idx_payment_methods_sort_order` ON `(is_active, sort_order)` WHERE `is_active = true`

**Enum Type:**
```sql
CREATE TYPE payment_method_type_enum AS ENUM ('BANK_TRANSFER', 'MOBILE_MONEY', 'OTHER');
```

---

### 3.10 payments

Payment submissions with screenshot and review information.

**Table:** `payments`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Payment identifier |
| `order_id` | BIGINT | NOT NULL, FK to orders.id | Associated order |
| `method_id` | BIGINT | NOT NULL, FK to payment_methods.id | Payment method used |
| `submitted_by_user_id` | UUID | NOT NULL, FK to users.id | User who submitted payment |
| `amount_declared` | DECIMAL(10,2) | NULL allowed, CHECK (amount_declared >= 0) | Amount declared by customer |
| `reference_text` | VARCHAR(200) | NULL allowed | Transaction reference |
| `paid_at` | TIMESTAMP | NULL allowed | Customer-reported payment date/time |
| `screenshot_url` | VARCHAR(500) | NOT NULL | Payment screenshot URL (MinIO/S3) |
| `status` | payment_status_enum | NOT NULL, DEFAULT 'submitted' | Payment review status |
| `reviewed_by` | UUID | NULL allowed, FK to users.id | User who reviewed payment |
| `reviewed_at` | TIMESTAMP | NULL allowed | Review timestamp |
| `review_note` | TEXT | NULL allowed | Review notes/reason |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Submission timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_payments_order_id` ON `order_id`
- `idx_payments_method_id` ON `method_id`
- `idx_payments_status` ON `status`
- `idx_payments_submitted_by` ON `submitted_by_user_id`
- `idx_payments_reviewed_by` ON `reviewed_by`
- `idx_payments_created_at` ON `created_at`
- Composite index: `idx_payments_status_created` ON `(status, created_at)` WHERE `status = 'submitted'` (for payment queue)

**Foreign Keys:**
- `order_id` REFERENCES `orders(id)` ON DELETE CASCADE
- `method_id` REFERENCES `payment_methods(id)` ON DELETE RESTRICT
- `submitted_by_user_id` REFERENCES `users(id)` ON DELETE RESTRICT
- `reviewed_by` REFERENCES `users(id)` ON DELETE SET NULL

**Enum Type:**
```sql
CREATE TYPE payment_status_enum AS ENUM (
    'submitted',
    'approved',
    'rejected',
    'resubmit_requested'
);
```

**Business Rules:**
- One active payment per order (application-level constraint)
- Payment status transitions: submitted → approved/rejected/resubmit_requested
- When payment approved, order status should transition to `PAID`

---

### 3.11 order_status_history

Audit trail for order status changes.

**Table:** `order_status_history`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | History entry identifier |
| `order_id` | BIGINT | NOT NULL, FK to orders.id | Order reference |
| `old_status` | order_status_enum | NULL allowed | Previous status |
| `new_status` | order_status_enum | NOT NULL | New status |
| `actor_user_id` | UUID | NULL allowed, FK to users.id | User who made the change |
| `note` | TEXT | NULL allowed | Change note/reason |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Change timestamp |

**Indexes:**
- `idx_order_status_history_order_id` ON `order_id`
- `idx_order_status_history_created_at` ON `created_at`
- Composite index: `idx_order_status_history_order_created` ON `(order_id, created_at)`

**Foreign Keys:**
- `order_id` REFERENCES `orders(id)` ON DELETE CASCADE
- `actor_user_id` REFERENCES `users(id)` ON DELETE SET NULL

**Notes:**
- All status changes should be logged here
- `old_status` can be NULL for initial status
- `actor_user_id` can be NULL for system-initiated changes

---

## 4. Supporting Tables

### 4.1 notifications

In-app notifications for users.

**Table:** `notifications`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Notification identifier |
| `user_id` | UUID | NOT NULL, FK to users.id | Recipient user |
| `type` | notification_type_enum | NOT NULL | Notification type |
| `title` | VARCHAR(200) | NOT NULL | Notification title |
| `message` | TEXT | NOT NULL | Notification message |
| `related_order_id` | BIGINT | NULL allowed, FK to orders.id | Related order (if applicable) |
| `related_payment_id` | BIGINT | NULL allowed, FK to payments.id | Related payment (if applicable) |
| `is_read` | BOOLEAN | NOT NULL, DEFAULT false | Read status |
| `read_at` | TIMESTAMP | NULL allowed | Read timestamp |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_notifications_user_id` ON `user_id`
- `idx_notifications_is_read` ON `(user_id, is_read)` WHERE `is_read = false`
- `idx_notifications_created_at` ON `created_at`
- `idx_notifications_related_order` ON `related_order_id`
- `idx_notifications_related_payment` ON `related_payment_id`

**Foreign Keys:**
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE
- `related_order_id` REFERENCES `orders(id)` ON DELETE CASCADE
- `related_payment_id` REFERENCES `payments(id)` ON DELETE CASCADE

**Enum Type:**
```sql
CREATE TYPE notification_type_enum AS ENUM (
    'PAYMENT_APPROVED',
    'PAYMENT_REJECTED',
    'PAYMENT_RESUBMIT_REQUESTED',
    'ORDER_STATUS_UPDATED',
    'ORDER_DISPATCHED',
    'ORDER_DELIVERED',
    'NEW_ORDER',
    'NEW_PAYMENT_SUBMITTED'
);
```

---

### 4.2 otp_codes

OTP codes for phone and email verification.

**Table:** `otp_codes`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | OTP identifier |
| `identifier` | VARCHAR(255) | NOT NULL | Phone number or email |
| `code` | VARCHAR(10) | NOT NULL | OTP code |
| `type` | otp_type_enum | NOT NULL | OTP type (phone/email) |
| `purpose` | otp_purpose_enum | NOT NULL | Purpose (login/verification) |
| `expires_at` | TIMESTAMP | NOT NULL | Expiration timestamp |
| `used_at` | TIMESTAMP | NULL allowed | Usage timestamp |
| `ip_address` | VARCHAR(45) | NULL allowed | Request IP address |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_otp_codes_identifier` ON `identifier`
- `idx_otp_codes_code` ON `code`
- `idx_otp_codes_expires_at` ON `expires_at`
- Composite index: `idx_otp_codes_identifier_type` ON `(identifier, type, expires_at)` WHERE `used_at IS NULL`

**Enum Types:**
```sql
CREATE TYPE otp_type_enum AS ENUM ('phone', 'email');
CREATE TYPE otp_purpose_enum AS ENUM ('login', 'verification', 'password_reset');
```

**Business Rules:**
- OTP codes expire after 5 minutes (configurable)
- OTP codes are single-use
- Rate limiting enforced application-side

---

### 4.3 refresh_tokens

JWT refresh tokens for session management.

**Table:** `refresh_tokens`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Token identifier |
| `user_id` | UUID | NOT NULL, FK to users.id | Token owner |
| `token` | VARCHAR(500) | NOT NULL, UNIQUE | Refresh token value |
| `expires_at` | TIMESTAMP | NOT NULL | Expiration timestamp |
| `revoked_at` | TIMESTAMP | NULL allowed | Revocation timestamp |
| `ip_address` | VARCHAR(45) | NULL allowed | Request IP address |
| `user_agent` | VARCHAR(500) | NULL allowed | User agent string |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_refresh_tokens_token` ON `token` (unique)
- `idx_refresh_tokens_user_id` ON `user_id`
- `idx_refresh_tokens_expires_at` ON `expires_at`

**Foreign Keys:**
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Business Rules:**
- Tokens expire after 7 days (configurable)
- Tokens can be revoked (logout)
- Token rotation on refresh (optional, application-level)

---

### 4.4 product_tags (Optional)

Tags for product categorization and search.

**Table:** `product_tags`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Tag identifier |
| `name` | VARCHAR(50) | NOT NULL, UNIQUE | Tag name |
| `slug` | VARCHAR(50) | NOT NULL, UNIQUE | URL-friendly identifier |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Table:** `product_tag_associations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `product_id` | BIGINT | NOT NULL, FK to products.id | Product reference |
| `tag_id` | BIGINT | NOT NULL, FK to product_tags.id | Tag reference |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Association timestamp |

**Primary Key:** `(product_id, tag_id)`

**Foreign Keys:**
- `product_id` REFERENCES `products(id)` ON DELETE CASCADE
- `tag_id` REFERENCES `product_tags(id)` ON DELETE CASCADE

**Indexes:**
- `idx_product_tag_associations_product` ON `product_id`
- `idx_product_tag_associations_tag` ON `tag_id`

---

## 5. Database Constraints and Business Rules

### 5.1 Referential Integrity

All foreign key relationships enforce referential integrity:
- **CASCADE:** Child records deleted when parent deleted (e.g., `order_items` when `order` deleted)
- **RESTRICT:** Prevent deletion if child records exist (e.g., `orders` when `user` has orders)
- **SET NULL:** Set foreign key to NULL when parent deleted (e.g., `delivery_zone_id` when zone deleted)

### 5.2 Data Validation

**Application-Level Validations:**
- Order total = subtotal + delivery_fee
- Order item line_total = quantity * unit_price
- Expected delivery dates: `expected_delivery_to >= expected_delivery_from`
- Delivery zone: `eta_max_days >= eta_min_days`
- Stock quantity: `stock_qty >= 0`
- Prices: `price >= 0`, `fee >= 0`

**Database-Level Constraints:**
- CHECK constraints for numeric ranges
- UNIQUE constraints for business keys
- NOT NULL constraints for required fields

### 5.3 Order Status State Machine

Valid status transitions (enforced application-side):

```
PENDING_PAYMENT
    ↓
PAYMENT_SUBMITTED
    ↓
PAYMENT_RESUBMIT_REQUESTED → PAYMENT_SUBMITTED (resubmit)
    ↓
PAYMENT_REJECTED
    ↓
PAID
    ↓
PACKING
    ↓
DISPATCHED
    ↓
DELIVERED

CANCELLED (can occur from any status except DELIVERED)
```

### 5.4 Payment Status Transitions

```
submitted
    ↓
approved / rejected / resubmit_requested
    ↓
(resubmit_requested) → submitted (resubmission)
```

### 5.5 Stock Management

- Stock quantity stored at `product_variants.stock_qty`
- Stock reservation strategy (configurable):
  - **Option 1:** Reserve on order placement (`PENDING_PAYMENT`)
  - **Option 2:** Reserve on payment approval (`PAID`)
- Stock released on order cancellation
- Stock decremented on order fulfillment (optional, if tracking sold units)

---

## 6. Indexing Strategy

### 6.1 Primary Indexes

All tables have primary key indexes (automatic in PostgreSQL).

### 6.2 Foreign Key Indexes

All foreign key columns are indexed for join performance:
- `user_id` in `orders`, `payments`, `notifications`, `refresh_tokens`
- `order_id` in `order_items`, `payments`, `order_status_history`
- `product_id` in `product_variants`, `product_images`, `order_items`
- `category_id` in `products`
- `delivery_zone_id` in `orders`
- `method_id` in `payments`

### 6.3 Query Optimization Indexes

**High-Frequency Queries:**
- `orders`: `(user_id, status)`, `(status, created_at)`
- `payments`: `(status, created_at)` WHERE `status = 'submitted'` (payment queue)
- `products`: `(is_active, deleted_at)` WHERE `is_active = true AND deleted_at IS NULL`
- `notifications`: `(user_id, is_read)` WHERE `is_read = false`
- `otp_codes`: `(identifier, type, expires_at)` WHERE `used_at IS NULL`

### 6.4 Partial Indexes

Partial indexes for filtered queries:
- Active products: `WHERE is_active = true AND deleted_at IS NULL`
- Active payment methods: `WHERE is_active = true`
- Unread notifications: `WHERE is_read = false`
- Unused OTP codes: `WHERE used_at IS NULL`
- Verified users: `WHERE phone_verified = true` or `email_verified = true`

---

## 7. Database Functions and Triggers

### 7.1 Updated_at Trigger

Automatically update `updated_at` timestamp on row modification.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Repeat for other tables: products, categories, orders, payment_methods, etc.
```

### 7.2 Order Status History Trigger

Automatically log status changes to `order_status_history`.

```sql
CREATE OR REPLACE FUNCTION log_order_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO order_status_history (order_id, old_status, new_status, actor_user_id)
        VALUES (NEW.id, OLD.status, NEW.status, NULL); -- actor_user_id set by application
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER order_status_change_log
    AFTER UPDATE OF status ON orders
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION log_order_status_change();
```

**Note:** `actor_user_id` should be set by application logic, not trigger.

---

## 8. Data Types and Enums

### 8.1 Custom Enum Types

```sql
-- User roles
CREATE TYPE user_role_enum AS ENUM ('customer', 'sales', 'admin');

-- Order statuses
CREATE TYPE order_status_enum AS ENUM (
    'PENDING_PAYMENT',
    'PAYMENT_SUBMITTED',
    'PAYMENT_RESUBMIT_REQUESTED',
    'PAYMENT_REJECTED',
    'PAID',
    'PACKING',
    'DISPATCHED',
    'DELIVERED',
    'CANCELLED'
);

-- Payment method types
CREATE TYPE payment_method_type_enum AS ENUM ('BANK_TRANSFER', 'MOBILE_MONEY', 'OTHER');

-- Payment statuses
CREATE TYPE payment_status_enum AS ENUM (
    'submitted',
    'approved',
    'rejected',
    'resubmit_requested'
);

-- Notification types
CREATE TYPE notification_type_enum AS ENUM (
    'PAYMENT_APPROVED',
    'PAYMENT_REJECTED',
    'PAYMENT_RESUBMIT_REQUESTED',
    'ORDER_STATUS_UPDATED',
    'ORDER_DISPATCHED',
    'ORDER_DELIVERED',
    'NEW_ORDER',
    'NEW_PAYMENT_SUBMITTED'
);

-- OTP types
CREATE TYPE otp_type_enum AS ENUM ('phone', 'email');

-- OTP purposes
CREATE TYPE otp_purpose_enum AS ENUM ('login', 'verification', 'password_reset');
```

### 8.2 Standard Data Types

- **UUID:** For `users.id` (security, distributed system readiness)
- **BIGSERIAL:** For high-volume tables (orders, products, payments)
- **DECIMAL(10,2):** For monetary values (prices, fees, totals)
- **VARCHAR:** For text fields with length limits
- **TEXT:** For unlimited text (descriptions, notes)
- **TIMESTAMP:** For date/time fields
- **DATE:** For date-only fields (delivery dates)
- **BOOLEAN:** For flags

---

## 9. Migration Strategy

### 9.1 Migration Tool

- **Tool:** Alembic (Python database migration tool)
- **Location:** Backend service migrations directory
- **Versioning:** Sequential migration files

### 9.2 Initial Migration Structure

1. Create enum types
2. Create core tables (users, categories, products, etc.)
3. Create supporting tables (notifications, otp_codes, etc.)
4. Create indexes
5. Create foreign keys
6. Create triggers and functions
7. Create initial admin user (seed data)

### 9.3 Migration Best Practices

- **Idempotent:** Migrations should be safe to run multiple times
- **Backward Compatible:** Avoid breaking changes in production
- **Tested:** Test migrations on staging before production
- **Rollback:** Provide down migrations for rollback capability
- **Data Migration:** Separate schema and data migrations

---

## 10. Performance Considerations

### 10.1 Query Optimization

- Use appropriate indexes for frequent queries
- Avoid N+1 queries (use eager loading)
- Use pagination for list endpoints
- Cache frequently accessed data (product catalog)

### 10.2 Connection Pooling

- Use connection pooling (SQLAlchemy pool)
- Configure pool size based on expected load
- Monitor connection usage

### 10.3 Database Maintenance

- Regular VACUUM and ANALYZE
- Monitor table bloat
- Archive old data (e.g., old notifications, expired OTP codes)

### 10.4 Scalability

- Current design supports baseline: 200 orders/day
- Future optimizations:
  - Read replicas for reporting
  - Partitioning for high-volume tables (if needed)
  - Materialized views for complex reports

---

## 11. Security Considerations

### 11.1 Data Protection

- **Sensitive Data:** Phone numbers, emails stored as-is (encryption at application level if required)
- **Passwords:** Not stored (OTP-based authentication)
- **Payment Screenshots:** Stored in MinIO/S3, URLs in database

### 11.2 Access Control

- Database user with minimal privileges
- Separate read/write users (future)
- Row-level security (optional, future)

### 11.3 Audit Trail

- `order_status_history` for order changes
- `payments.reviewed_by`, `payments.reviewed_at` for payment reviews
- `created_at`, `updated_at` timestamps on all tables

---

## 12. Backup and Recovery

### 12.1 Backup Strategy

- **Full Backups:** Daily automated backups
- **Incremental Backups:** Hourly (optional)
- **Retention:** 30 days (configurable)

### 12.2 Backup Methods

- PostgreSQL `pg_dump` for full backups
- Continuous archiving (WAL) for point-in-time recovery
- Backup storage separate from primary database

### 12.3 Recovery Procedures

- Test restore procedures regularly
- Document recovery steps
- Maintain backup verification

---

## 13. Future Enhancements

### 13.1 Potential Schema Additions

- **discount_codes:** For promotional codes
- **couriers:** For courier assignment and tracking
- **branches:** For multi-branch inventory
- **inventory_transactions:** For detailed stock movement tracking
- **reviews:** For product reviews and ratings
- **addresses:** For saved customer addresses

### 13.2 Performance Enhancements

- Materialized views for reporting
- Full-text search indexes for product search
- Partitioning for high-volume tables
- Read replicas for analytics

---

**Document Status:** Draft v1.0  
**Last Updated:** Based on SRS v1.0 & Architecture Design v1.0  
**Next Review:** After implementation decisions are made

