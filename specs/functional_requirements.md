# Functional Requirements Document

**Project Name:** Melegna Foods Commerce & Order Operations Platform  
**Version:** 1.0  
**Based on:** Software Requirements Specification v1.0, Architecture Design v1.0, Database Design v1.0

---

## 1. Document Overview

### 1.1 Purpose

This document provides detailed functional requirements for the Melegna Foods Commerce & Order Operations Platform. It specifies what the system must do from a user perspective, organized by functional areas and user roles.

### 1.2 Scope

This document covers all functional requirements for:
- Customer-facing features (storefront)
- Admin and Sales user features (dashboard)
- Authentication and user management
- Product catalog management
- Order processing and fulfillment
- Payment workflow
- Notifications
- Reporting

### 1.3 User Roles

- **Customer:** End user who browses products and places orders
- **Sales:** Internal staff who verify payments and update order statuses
- **Admin:** Full system administrator with all permissions

---

## 2. Authentication and User Management

### 2.1 Phone OTP Authentication (Primary)

#### FR-AUTH-1.1 Request OTP

**Description:** Users can request an OTP code via phone number for authentication.

**Actor:** Customer, Sales, Admin

**Preconditions:**
- User is not authenticated
- Phone number is provided

**Main Flow:**
1. User enters phone number on login page
2. System validates phone number format
3. System checks rate limiting (max requests per phone/IP per time period)
4. System generates OTP code (6-digit numeric)
5. System stores OTP in `otp_codes` table with expiration (5 minutes)
6. System sends OTP via configured provider (SMS gateway, dev mode, etc.)
7. System returns success response

**Postconditions:**
- OTP code stored in database with expiration timestamp
- OTP sent to user's phone number
- Rate limiting counter incremented

**Alternative Flows:**
- **A1:** Rate limit exceeded → Return error message
- **A2:** Invalid phone format → Return validation error
- **A3:** Dev mode → OTP displayed in response/logs instead of SMS

**Business Rules:**
- OTP expires after 5 minutes (configurable)
- OTP is single-use
- Rate limit: Max 3 requests per phone per 15 minutes
- Rate limit: Max 5 requests per IP per 15 minutes

**Data Requirements:**
- Store in `otp_codes` table: `identifier` (phone), `code`, `type` ('phone'), `purpose` ('login'), `expires_at`, `ip_address`

---

#### FR-AUTH-1.2 Verify OTP and Login

**Description:** Users verify OTP code and receive JWT tokens for authentication.

**Actor:** Customer, Sales, Admin

**Preconditions:**
- User has requested OTP
- OTP code is provided
- OTP is not expired

**Main Flow:**
1. User enters phone number and OTP code
2. System validates OTP code against database
3. System checks OTP expiration
4. System checks if OTP already used
5. System looks up user by phone number
6. If user exists:
   - Update `phone_verified = true` if not already verified
   - Mark OTP as used (`used_at = CURRENT_TIMESTAMP`)
7. If user does not exist:
   - Create new user with `phone`, `phone_verified = true`, `role = 'customer'`
   - Mark OTP as used
8. System generates JWT access token (15 minutes expiry)
9. System generates JWT refresh token (7 days expiry)
10. System stores refresh token in `refresh_tokens` table
11. System returns tokens to client

**Postconditions:**
- User authenticated and logged in
- JWT tokens issued
- OTP marked as used
- User record created or updated

**Alternative Flows:**
- **A1:** Invalid OTP → Return error "Invalid OTP code"
- **A2:** Expired OTP → Return error "OTP expired. Please request a new one"
- **A3:** OTP already used → Return error "OTP already used"
- **A4:** OTP not found → Return error "Invalid OTP code"

**Business Rules:**
- OTP can only be used once
- OTP must be verified within expiration period
- New users default to 'customer' role
- Admin must assign 'sales' or 'admin' roles manually

**Data Requirements:**
- Update `otp_codes.used_at`
- Create/update `users` record
- Create `refresh_tokens` record

---

### 2.2 Email Authentication (Backup)

#### FR-AUTH-2.1 Request Email OTP/Magic Link

**Description:** Users can request email-based authentication (OTP or magic link - implementation decision).

**Actor:** Customer, Sales, Admin

**Preconditions:**
- User is not authenticated
- Email address is provided

**Main Flow:**
1. User enters email address on login page
2. System validates email format
3. System checks rate limiting
4. **If OTP approach:**
   - Generate OTP code
   - Store in `otp_codes` table with `type = 'email'`
   - Send OTP via email
5. **If magic link approach:**
   - Generate secure token
   - Create verification link with token
   - Send link via email
6. System returns success response

**Postconditions:**
- OTP/magic link sent to email
- Rate limiting applied

**Business Rules:**
- Same rate limiting as phone OTP
- Email OTP expires after 5 minutes
- Magic link expires after 15 minutes

---

#### FR-AUTH-2.2 Verify Email and Login

**Description:** Users verify email OTP/magic link and receive JWT tokens.

**Actor:** Customer, Sales, Admin

**Main Flow:**
1. User provides email and OTP code OR clicks magic link
2. System validates OTP/token
3. System checks expiration
4. System looks up or creates user
5. System updates `email_verified = true`
6. System issues JWT tokens
7. System stores refresh token

**Postconditions:**
- User authenticated
- Email verified
- Tokens issued

---

### 2.3 Telegram Authentication

#### FR-AUTH-3.1 Verify Telegram initData

**Description:** System validates Telegram WebApp initData signature and links/creates user account.

**Actor:** Customer (via Telegram Mini App)

**Preconditions:**
- User accessing via Telegram Mini App
- Telegram initData provided

**Main Flow:**
1. Frontend sends Telegram initData to backend
2. System validates initData signature using Telegram secret
3. System extracts user data: `telegram_user_id`, `username`, `first_name`, `last_name`
4. System checks timestamp (prevent replay attacks)
5. System looks up user by `telegram_user_id`
6. **If user exists:**
   - Update Telegram fields if changed
   - Issue JWT tokens
7. **If user does not exist:**
   - Create "telegram-only" session
   - If configured to require phone verification:
     - Prompt user to link phone via OTP
     - Allow browsing only until phone verified
   - If configured to allow browsing:
     - Create user with Telegram data
     - Issue JWT tokens with limited permissions
8. System stores refresh token

**Postconditions:**
- Telegram account linked/created
- User authenticated (with appropriate permissions)

**Business Rules:**
- Telegram initData signature must be valid
- Timestamp must be recent (within 24 hours)
- If phone verification required, user cannot place orders until phone verified
- One Telegram user ID can link to one internal user account

**Data Requirements:**
- Create/update `users` record with Telegram fields
- Create `refresh_tokens` record

---

### 2.4 Account Linking

#### FR-AUTH-4.1 Link Phone to Telegram Account

**Description:** User with Telegram-only account links phone number via OTP.

**Actor:** Customer

**Preconditions:**
- User authenticated via Telegram
- User does not have verified phone

**Main Flow:**
1. User requests phone OTP
2. User verifies OTP
3. System checks if phone already linked to another account
4. **If phone available:**
   - Update user record with phone and `phone_verified = true`
   - Grant full customer permissions
5. **If phone linked to another account:**
   - Return error "Phone number already linked to another account"
   - Optionally offer account merge (future feature)

**Postconditions:**
- Phone linked to user account
- User has full customer permissions

**Business Rules:**
- Phone must be unique when verified
- Cannot link phone already linked to another account

---

### 2.5 Token Management

#### FR-AUTH-5.1 Refresh Access Token

**Description:** User refreshes expired access token using refresh token.

**Actor:** Customer, Sales, Admin

**Preconditions:**
- User has valid refresh token
- Access token expired

**Main Flow:**
1. Client sends refresh token to `/auth/refresh`
2. System validates refresh token
3. System checks token expiration
4. System checks if token revoked
5. System looks up user
6. System generates new access token
7. System optionally rotates refresh token (implementation decision)
8. System returns new tokens

**Postconditions:**
- New access token issued
- User session continues

**Alternative Flows:**
- **A1:** Invalid refresh token → Return 401 Unauthorized
- **A2:** Token expired → Return 401 Unauthorized
- **A3:** Token revoked → Return 401 Unauthorized

---

#### FR-AUTH-5.2 Logout

**Description:** User logs out and invalidates refresh token.

**Actor:** Customer, Sales, Admin

**Main Flow:**
1. User clicks logout
2. System receives refresh token
3. System marks refresh token as revoked (`revoked_at = CURRENT_TIMESTAMP`)
4. System returns success

**Postconditions:**
- Refresh token invalidated
- User logged out

---

### 2.6 User Management (Admin)

#### FR-AUTH-6.1 Create Sales/Admin User

**Description:** Admin creates new Sales or Admin user account.

**Actor:** Admin

**Preconditions:**
- Admin authenticated
- Admin role required

**Main Flow:**
1. Admin navigates to Users management page
2. Admin clicks "Create User"
3. Admin enters: phone, email (optional), name, role (sales/admin)
4. System validates input
5. System checks phone/email uniqueness
6. System creates user with specified role
7. System sends OTP to phone for initial verification
8. System returns success

**Postconditions:**
- New user created
- OTP sent for verification

**Business Rules:**
- Only Admin can create Sales/Admin users
- Phone must be unique
- Email must be unique if provided

---

#### FR-AUTH-6.2 Update User Role

**Description:** Admin updates user role.

**Actor:** Admin

**Main Flow:**
1. Admin selects user
2. Admin changes role
3. System validates role change
4. System updates user role
5. System logs role change (audit trail)

**Postconditions:**
- User role updated
- Change logged

**Business Rules:**
- Cannot change own role
- Cannot remove last admin

---

## 3. Product Catalog Management

### 3.1 Product Management (Admin)

#### FR-PROD-1.1 Create Product

**Description:** Admin creates a new product in the catalog.

**Actor:** Admin

**Preconditions:**
- Admin authenticated
- Admin role required

**Main Flow:**
1. Admin navigates to Products page
2. Admin clicks "Create Product"
3. Admin enters:
   - Name (required)
   - Description (optional)
   - Category (optional)
   - Tags (optional)
   - Is Featured (boolean)
   - Is Active (boolean, default true)
4. System validates input
5. System generates slug from name (URL-friendly)
6. System checks slug uniqueness
7. System creates product in `products` table
8. System returns product details

**Postconditions:**
- Product created in database
- Product available for variant creation

**Business Rules:**
- Product name required
- Slug must be unique
- Product must have at least one variant to be orderable

**Data Requirements:**
- Create record in `products` table
- Set `is_active = true` by default
- Set `deleted_at = NULL`

---

#### FR-PROD-1.2 Update Product

**Description:** Admin updates existing product information.

**Actor:** Admin

**Main Flow:**
1. Admin selects product
2. Admin modifies fields
3. System validates changes
4. System updates product record
5. System updates `updated_at` timestamp
6. System returns updated product

**Postconditions:**
- Product information updated

**Business Rules:**
- Cannot change slug if product has orders (maintain historical accuracy)
- Soft delete: Set `deleted_at` instead of hard delete

---

#### FR-PROD-1.3 Delete Product (Soft Delete)

**Description:** Admin soft-deletes a product.

**Actor:** Admin

**Main Flow:**
1. Admin selects product
2. Admin clicks "Delete"
3. System confirms deletion
4. System sets `deleted_at = CURRENT_TIMESTAMP`
5. System sets `is_active = false`
6. System returns success

**Postconditions:**
- Product soft-deleted
- Product not visible in customer catalog
- Historical orders remain intact

**Business Rules:**
- Soft delete only (never hard delete)
- Product with active orders can be deleted (historical preservation)

---

#### FR-PROD-1.4 Upload Product Images

**Description:** Admin uploads images for a product.

**Actor:** Admin

**Preconditions:**
- Product exists

**Main Flow:**
1. Admin selects product
2. Admin uploads image files (jpg/png)
3. System validates file type and size
4. System uploads to MinIO/S3
5. System creates records in `product_images` table
6. System sets `sort_order` (sequence of upload or manual)
7. System returns image URLs

**Postconditions:**
- Images stored in object storage
- Image records created in database

**Business Rules:**
- File types: jpg, png only
- Max file size: 5MB per image
- Max images per product: 10 (configurable)
- First image is primary (or manually set)

**Data Requirements:**
- Create records in `product_images` table
- Store URLs in `url` column

---

### 3.2 Product Variant Management

#### FR-PROD-2.1 Create Product Variant

**Description:** Admin creates a variant for a product (size, weight, package).

**Actor:** Admin

**Preconditions:**
- Product exists

**Main Flow:**
1. Admin selects product
2. Admin clicks "Add Variant"
3. Admin enters:
   - Label (e.g., "250g", "1kg pack") (required)
   - Price (required, >= 0)
   - Stock Quantity (default 0, >= 0)
   - SKU (optional, unique)
   - Is Active (default true)
4. System validates input
5. System checks label uniqueness per product
6. System checks SKU uniqueness (if provided)
7. System creates variant in `product_variants` table
8. System returns variant details

**Postconditions:**
- Variant created
- Product can be ordered with this variant

**Business Rules:**
- Variant label must be unique per product
- SKU must be unique across all variants
- Price must be >= 0
- Stock quantity must be >= 0

**Data Requirements:**
- Create record in `product_variants` table

---

#### FR-PROD-2.2 Update Variant Stock

**Description:** Admin updates stock quantity for a variant.

**Actor:** Admin

**Main Flow:**
1. Admin selects variant
2. Admin updates stock quantity
3. System validates quantity >= 0
4. System updates `stock_qty` in database
5. System updates `updated_at` timestamp
6. System returns updated variant

**Postconditions:**
- Stock quantity updated

**Business Rules:**
- Stock cannot be negative
- Stock updates are immediate (no pending reservations)

---

### 3.3 Category Management

#### FR-PROD-3.1 Create Category

**Description:** Admin creates a product category.

**Actor:** Admin

**Main Flow:**
1. Admin navigates to Categories page
2. Admin clicks "Create Category"
3. Admin enters:
   - Name (required, unique)
   - Description (optional)
   - Parent Category (optional, for hierarchy)
   - Sort Order (default 0)
   - Is Active (default true)
4. System validates input
5. System generates slug from name
6. System creates category in `categories` table
7. System returns category details

**Postconditions:**
- Category created
- Products can be assigned to category

**Business Rules:**
- Category name must be unique
- Parent category must exist (if provided)

---

### 3.4 Customer Product Browsing

#### FR-PROD-4.1 List Products

**Description:** Customer browses list of available products.

**Actor:** Customer (unauthenticated allowed)

**Preconditions:**
- None (public endpoint)

**Main Flow:**
1. Customer navigates to products page
2. System queries `products` table:
   - `is_active = true`
   - `deleted_at IS NULL`
   - Join with `product_variants` for availability
3. System applies filters (if provided):
   - Category
   - Search term (name, description)
   - Tags
   - Price range
   - In stock only
4. System applies pagination
5. System returns product list with:
   - Basic info (name, description, images)
   - Price range (min/max from variants)
   - Stock availability
   - Category

**Postconditions:**
- Product list displayed

**Business Rules:**
- Only active, non-deleted products shown
- Products with no active variants not shown
- Pagination: 20 items per page (configurable)

**Data Requirements:**
- Query `products`, `product_variants`, `product_images`, `categories` tables

---

#### FR-PROD-4.2 View Product Detail

**Description:** Customer views detailed product information.

**Actor:** Customer (unauthenticated allowed)

**Preconditions:**
- Product exists and is active

**Main Flow:**
1. Customer clicks on product
2. System queries product details:
   - Product information
   - All active variants with prices and stock
   - Product images
   - Category
   - Tags
3. System returns product detail

**Postconditions:**
- Product detail displayed

**Business Rules:**
- Show only active variants
- Display stock availability per variant
- Show "Out of Stock" if all variants out of stock

---

## 4. Order Management

### 4.1 Shopping Cart (Client-Side)

**Note:** Cart management is client-side (browser storage). Backend receives cart data on checkout.

---

### 4.2 Order Placement

#### FR-ORD-1.1 Create Order (Checkout)

**Description:** Customer creates an order from cart items.

**Actor:** Customer

**Preconditions:**
- Customer authenticated
- Cart has items
- All items in stock

**Main Flow:**
1. Customer proceeds to checkout
2. Customer enters:
   - Delivery address (required)
   - Recipient name (required)
   - Recipient phone (required, auto-filled from account, editable)
   - Delivery instructions (optional)
   - Delivery zone (selected or auto-detected)
3. System validates input
4. System validates cart items:
   - Products exist and are active
   - Variants exist and are active
   - Stock available for requested quantities
5. System calculates:
   - Subtotal (sum of line totals)
   - Delivery fee (from `delivery_zones` table)
   - Total (subtotal + delivery fee)
6. System calculates expected delivery dates:
   - `expected_delivery_from = CURRENT_DATE + zone.eta_min_days`
   - `expected_delivery_to = CURRENT_DATE + zone.eta_max_days`
7. System generates unique order number: `ORD-{YYYYMMDD}-{sequential}`
8. System creates order in `orders` table with status `PENDING_PAYMENT`
9. System creates order items in `order_items` table:
   - Store product name and variant label as snapshots
   - Store unit price at time of order
   - Calculate line total
10. **If stock reservation on order placement:**
    - System reserves stock (decrement `stock_qty`)
    - Lock stock for this order
11. System creates initial status history entry
12. System returns order details with payment instructions

**Postconditions:**
- Order created
- Order status: `PENDING_PAYMENT`
- Stock reserved (if configured)
- Order number generated

**Alternative Flows:**
- **A1:** Item out of stock → Return error "Item no longer available"
- **A2:** Stock changed during checkout → Return error "Stock updated. Please refresh"
- **A3:** Invalid delivery zone → Return error "Invalid delivery zone"

**Business Rules:**
- Order number must be unique
- Stock validation must be atomic (prevent race conditions)
- Order total = subtotal + delivery fee
- Cannot order more than available stock

**Data Requirements:**
- Create record in `orders` table
- Create records in `order_items` table
- Create record in `order_status_history` table
- Update `product_variants.stock_qty` (if reservation on placement)

---

#### FR-ORD-1.2 Display Payment Instructions

**Description:** System displays payment methods and instructions after order creation.

**Actor:** Customer

**Preconditions:**
- Order created
- Order status: `PENDING_PAYMENT`

**Main Flow:**
1. System queries active payment methods from `payment_methods` table:
   - `is_active = true`
   - Ordered by `sort_order`
2. System displays:
   - Order number
   - Total amount (items + delivery)
   - Expected delivery window
   - List of payment methods with:
     - Method name
     - Account number/wallet ID (copyable)
     - Account holder name
     - Instructions
3. System provides upload interface for payment screenshot

**Postconditions:**
- Payment instructions displayed
- Customer can proceed to payment upload

**Business Rules:**
- Only active payment methods shown
- Methods sorted by `sort_order`

---

### 4.3 Order Tracking

#### FR-ORD-2.1 View My Orders

**Description:** Customer views list of their orders.

**Actor:** Customer

**Preconditions:**
- Customer authenticated

**Main Flow:**
1. Customer navigates to "My Orders"
2. System queries `orders` table:
   - `user_id = current_user.id`
   - Ordered by `created_at DESC`
3. System applies pagination
4. System returns order list with:
   - Order number
   - Order date
   - Status
   - Total amount
   - Delivery address (truncated)

**Postconditions:**
- Order list displayed

**Business Rules:**
- Only customer's own orders visible
- Pagination: 10 orders per page

---

#### FR-ORD-2.2 View Order Detail

**Description:** Customer views detailed order information with status timeline.

**Actor:** Customer

**Preconditions:**
- Order exists
- Order belongs to customer

**Main Flow:**
1. Customer clicks on order
2. System queries order details:
   - Order information
   - Order items (with snapshots)
   - Payment information (if submitted)
   - Status history timeline
3. System returns order detail

**Postconditions:**
- Order detail displayed with timeline

**Business Rules:**
- Customer can only view own orders
- Payment screenshot visible if payment submitted

---

### 4.4 Order Cancellation

#### FR-ORD-3.1 Cancel Order (Customer)

**Description:** Customer cancels their order.

**Actor:** Customer

**Preconditions:**
- Order exists
- Order belongs to customer
- Order status: `PENDING_PAYMENT`
- No payment submitted OR payment not approved

**Main Flow:**
1. Customer clicks "Cancel Order"
2. System validates cancellation eligibility
3. System updates order:
   - Status: `CANCELLED`
   - `cancelled_at = CURRENT_TIMESTAMP`
   - `cancellation_reason = "Cancelled by customer"`
4. System logs status change
5. **If stock was reserved:**
   - System releases stock (increment `stock_qty`)
6. System creates notification for customer
7. System returns success

**Postconditions:**
- Order cancelled
- Stock released (if reserved)
- Status history updated

**Business Rules:**
- Customer can only cancel in `PENDING_PAYMENT` status
- Cannot cancel if payment approved
- Stock must be released if reserved

---

#### FR-ORD-3.2 Cancel Order (Sales/Admin)

**Description:** Sales or Admin cancels any order with reason.

**Actor:** Sales, Admin

**Preconditions:**
- Order exists
- User has Sales or Admin role

**Main Flow:**
1. Sales/Admin selects order
2. Sales/Admin clicks "Cancel Order"
3. Sales/Admin enters cancellation reason (required)
4. Sales/Admin selects whether to restock (if applicable)
5. System validates order can be cancelled (not DELIVERED)
6. System updates order:
   - Status: `CANCELLED`
   - `cancelled_at = CURRENT_TIMESTAMP`
   - `cancellation_reason = provided reason`
7. System logs status change with actor
8. **If restock selected:**
   - System releases stock
9. System creates notification for customer
10. System returns success

**Postconditions:**
- Order cancelled
- Reason recorded
- Stock released (if selected)
- Customer notified

**Business Rules:**
- Cannot cancel DELIVERED orders
- Cancellation reason required
- Stock release optional

---

## 5. Payment Workflow

### 5.1 Payment Method Management (Admin)

#### FR-PAY-1.1 Create Payment Method

**Description:** Admin creates a new payment method (bank account, mobile wallet).

**Actor:** Admin

**Preconditions:**
- Admin authenticated

**Main Flow:**
1. Admin navigates to Payment Methods page
2. Admin clicks "Create Payment Method"
3. Admin enters:
   - Type (BANK_TRANSFER, MOBILE_MONEY, OTHER)
   - Name (e.g., "CBE Bank")
   - Account Identifier (account number/wallet ID)
   - Account Holder Name
   - Instructions (optional)
   - Sort Order (default 0)
   - Is Active (default true)
4. System validates input
5. System creates payment method in `payment_methods` table
6. System returns payment method details

**Postconditions:**
- Payment method created
- Available for customer selection

**Business Rules:**
- Payment method name should be descriptive
- Account identifier required

---

#### FR-PAY-1.2 Update Payment Method

**Description:** Admin updates payment method information.

**Actor:** Admin

**Main Flow:**
1. Admin selects payment method
2. Admin modifies fields
3. System validates changes
4. System updates `payment_methods` record
5. System returns updated payment method

**Postconditions:**
- Payment method updated

---

### 5.2 Payment Submission

#### FR-PAY-2.1 Upload Payment Screenshot

**Description:** Customer uploads payment screenshot and submits payment information.

**Actor:** Customer

**Preconditions:**
- Order exists
- Order status: `PENDING_PAYMENT` or `PAYMENT_RESUBMIT_REQUESTED`
- Customer owns order

**Main Flow:**
1. Customer navigates to order payment page
2. Customer selects payment method
3. Customer uploads screenshot (jpg/png)
4. Customer optionally enters:
   - Paid amount
   - Transaction reference
   - Paid date/time
5. System validates:
   - File type (jpg/png only)
   - File size (max 5MB)
   - Order status allows payment submission
6. System uploads file to MinIO/S3
7. System generates file URL
8. System creates payment record in `payments` table:
   - `order_id`
   - `method_id`
   - `submitted_by_user_id = current_user.id`
   - `screenshot_url`
   - `amount_declared` (if provided)
   - `reference_text` (if provided)
   - `paid_at` (if provided)
   - `status = 'submitted'`
9. System updates order status: `PAYMENT_SUBMITTED`
10. System logs status change
11. System creates notification for Sales/Admin: `NEW_PAYMENT_SUBMITTED`
12. System returns success

**Postconditions:**
- Payment submitted
- Order status: `PAYMENT_SUBMITTED`
- Screenshot stored
- Sales/Admin notified

**Alternative Flows:**
- **A1:** Invalid file type → Return error "Only JPG and PNG images allowed"
- **A2:** File too large → Return error "File size exceeds 5MB limit"
- **A3:** Order status invalid → Return error "Payment cannot be submitted for this order"

**Business Rules:**
- Only one active payment per order (if resubmission, mark previous as replaced)
- File must be image (jpg/png)
- Max file size: 5MB
- Payment can be submitted in `PENDING_PAYMENT` or `PAYMENT_RESUBMIT_REQUESTED` status

**Data Requirements:**
- Create record in `payments` table
- Update `orders.status`
- Create record in `order_status_history`
- Create notification in `notifications` table

---

### 5.3 Payment Review Queue

#### FR-PAY-3.1 View Payment Queue

**Description:** Sales/Admin views list of payments awaiting review.

**Actor:** Sales, Admin

**Preconditions:**
- User authenticated
- User has Sales or Admin role

**Main Flow:**
1. Sales/Admin navigates to Payment Queue
2. System queries `payments` table:
   - `status = 'submitted'`
   - Ordered by `created_at ASC` (oldest first)
3. System applies filters (if provided):
   - Date range
   - Amount range
   - Payment method
   - Customer
   - Order status
4. System returns payment list with:
   - Order number
   - Customer name
   - Payment method
   - Amount declared
   - Submission date
   - Order total

**Postconditions:**
- Payment queue displayed

**Business Rules:**
- Only payments with `status = 'submitted'` shown
- Ordered by submission date (oldest first)

---

#### FR-PAY-3.2 View Payment Detail

**Description:** Sales/Admin views payment details with screenshot.

**Actor:** Sales, Admin

**Preconditions:**
- Payment exists

**Main Flow:**
1. Sales/Admin clicks on payment
2. System queries payment details:
   - Payment information
   - Order details
   - Order items
   - Customer information
   - Screenshot (display inline)
3. System returns payment detail

**Postconditions:**
- Payment detail displayed with screenshot

---

#### FR-PAY-3.3 Approve Payment

**Description:** Sales/Admin approves a payment submission.

**Actor:** Sales, Admin

**Preconditions:**
- Payment exists
- Payment status: `submitted`
- User has Sales or Admin role

**Main Flow:**
1. Sales/Admin reviews payment and screenshot
2. Sales/Admin clicks "Approve"
3. Sales/Admin optionally enters review note
4. System validates payment can be approved
5. System updates payment:
   - `status = 'approved'`
   - `reviewed_by = current_user.id`
   - `reviewed_at = CURRENT_TIMESTAMP`
   - `review_note = provided note`
6. System updates order:
   - `status = 'PAID'`
7. System logs order status change
8. **If stock reservation on payment approval:**
   - System reserves stock (decrement `stock_qty`)
9. System creates notification for customer: `PAYMENT_APPROVED`
10. System creates notification for Sales/Admin: Order status updated
11. System returns success

**Postconditions:**
- Payment approved
- Order status: `PAID`
- Stock reserved (if configured)
- Customer notified

**Business Rules:**
- Only `submitted` payments can be approved
- Order status transitions to `PAID`
- Stock reservation occurs if configured for payment approval

**Data Requirements:**
- Update `payments` record
- Update `orders.status`
- Create `order_status_history` record
- Update `product_variants.stock_qty` (if reservation on approval)
- Create notifications

---

#### FR-PAY-3.4 Reject Payment

**Description:** Sales/Admin rejects a payment submission with reason.

**Actor:** Sales, Admin

**Preconditions:**
- Payment exists
- Payment status: `submitted`

**Main Flow:**
1. Sales/Admin reviews payment
2. Sales/Admin clicks "Reject"
3. Sales/Admin enters rejection reason (required)
4. System validates payment can be rejected
5. System updates payment:
   - `status = 'rejected'`
   - `reviewed_by = current_user.id`
   - `reviewed_at = CURRENT_TIMESTAMP`
   - `review_note = rejection reason`
6. System updates order:
   - `status = 'PAYMENT_REJECTED'`
7. System logs order status change
8. System creates notification for customer: `PAYMENT_REJECTED` (with reason)
9. System returns success

**Postconditions:**
- Payment rejected
- Order status: `PAYMENT_REJECTED`
- Customer notified with reason

**Business Rules:**
- Rejection reason required
- Customer can see rejection reason

---

#### FR-PAY-3.5 Request Payment Resubmission

**Description:** Sales/Admin requests customer to resubmit payment.

**Actor:** Sales, Admin

**Preconditions:**
- Payment exists
- Payment status: `submitted`

**Main Flow:**
1. Sales/Admin clicks "Request Resubmission"
2. Sales/Admin enters note (optional, e.g., "Screenshot unclear")
3. System updates payment:
   - `status = 'resubmit_requested'`
   - `reviewed_by = current_user.id`
   - `reviewed_at = CURRENT_TIMESTAMP`
   - `review_note = provided note`
4. System updates order:
   - `status = 'PAYMENT_RESUBMIT_REQUESTED'`
5. System logs order status change
6. System creates notification for customer: `PAYMENT_RESUBMIT_REQUESTED` (with note)
7. System returns success

**Postconditions:**
- Payment resubmission requested
- Order status: `PAYMENT_RESUBMIT_REQUESTED`
- Customer can upload new screenshot

**Business Rules:**
- Customer can submit new payment when status is `PAYMENT_RESUBMIT_REQUESTED`

---

## 6. Order Fulfillment

### 6.1 Order Status Updates

#### FR-FUL-1.1 Update Order Status (Packing)

**Description:** Sales/Admin updates order status to PACKING.

**Actor:** Sales, Admin

**Preconditions:**
- Order exists
- Order status: `PAID`

**Main Flow:**
1. Sales/Admin selects order
2. Sales/Admin clicks "Mark as Packing"
3. System validates status transition
4. System updates order:
   - `status = 'PACKING'`
5. System logs status change with actor
6. System creates notification for customer: `ORDER_STATUS_UPDATED`
7. System returns success

**Postconditions:**
- Order status: `PACKING`
- Status change logged
- Customer notified

**Business Rules:**
- Only valid status transitions allowed
- Status transitions enforced by state machine

---

#### FR-FUL-1.2 Update Order Status (Dispatched)

**Description:** Sales/Admin updates order status to DISPATCHED.

**Actor:** Sales, Admin

**Preconditions:**
- Order exists
- Order status: `PACKING`

**Main Flow:**
1. Sales/Admin selects order
2. Sales/Admin clicks "Mark as Dispatched"
3. System validates status transition
4. System updates order:
   - `status = 'DISPATCHED'`
5. System logs status change
6. System creates notification for customer: `ORDER_DISPATCHED`
7. System returns success

**Postconditions:**
- Order status: `DISPATCHED`
- Customer notified

---

#### FR-FUL-1.3 Mark Order as Delivered

**Description:** Sales/Admin marks order as DELIVERED with optional proof.

**Actor:** Sales, Admin

**Preconditions:**
- Order exists
- Order status: `DISPATCHED`

**Main Flow:**
1. Sales/Admin selects order
2. Sales/Admin clicks "Mark as Delivered"
3. Sales/Admin optionally:
   - Enters delivery note
   - Uploads delivery proof image
4. System validates status transition
5. System updates order:
   - `status = 'DELIVERED'`
6. System stores delivery proof (if provided) in MinIO/S3
7. System logs status change
8. System creates notification for customer: `ORDER_DELIVERED`
9. System returns success

**Postconditions:**
- Order status: `DELIVERED`
- Delivery proof stored (if provided)
- Customer notified

**Business Rules:**
- Delivery proof optional but recommended
- Order cannot be cancelled once DELIVERED

---

### 6.2 Delivery Zone Management (Admin)

#### FR-FUL-2.1 Create Delivery Zone

**Description:** Admin creates a delivery zone with fee and ETA.

**Actor:** Admin

**Main Flow:**
1. Admin navigates to Delivery Zones page
2. Admin clicks "Create Zone"
3. Admin enters:
   - Name (required, unique)
   - Description (optional)
   - Delivery Fee (required, >= 0)
   - ETA Min Days (required, >= 0)
   - ETA Max Days (required, >= min_days)
   - Is Active (default true)
4. System validates input
5. System creates zone in `delivery_zones` table
6. System returns zone details

**Postconditions:**
- Delivery zone created
- Available for order placement

**Business Rules:**
- Zone name must be unique
- `eta_max_days >= eta_min_days`
- Fee must be >= 0

---

#### FR-FUL-2.2 Calculate Delivery Fee and ETA

**Description:** System calculates delivery fee and expected delivery dates based on zone.

**Actor:** System (during order placement)

**Preconditions:**
- Delivery zone selected
- Zone exists and is active

**Main Flow:**
1. System looks up delivery zone
2. System retrieves:
   - `fee`
   - `eta_min_days`
   - `eta_max_days`
3. System calculates:
   - `delivery_fee = zone.fee`
   - `expected_delivery_from = CURRENT_DATE + zone.eta_min_days`
   - `expected_delivery_to = CURRENT_DATE + zone.eta_max_days`
4. System returns calculated values

**Postconditions:**
- Delivery fee calculated
- Expected delivery dates calculated

**Business Rules:**
- Only active zones used
- ETA calculated from order date

---

## 7. Notifications

### 7.1 In-App Notifications

#### FR-NOTIF-1.1 Create Notification

**Description:** System creates in-app notification for user.

**Actor:** System

**Preconditions:**
- User exists
- Notification event occurred

**Main Flow:**
1. System determines notification type and recipient
2. System creates notification in `notifications` table:
   - `user_id`
   - `type` (from enum)
   - `title`
   - `message`
   - `related_order_id` (if applicable)
   - `related_payment_id` (if applicable)
   - `is_read = false`
3. System optionally sends real-time update (WebSocket/SSE)

**Postconditions:**
- Notification created
- User can view notification

**Business Rules:**
- Notifications persist in database
- Notifications marked as unread by default

---

#### FR-NOTIF-1.2 View Notifications

**Description:** User views their notifications.

**Actor:** Customer, Sales, Admin

**Preconditions:**
- User authenticated

**Main Flow:**
1. User navigates to Notifications
2. System queries `notifications` table:
   - `user_id = current_user.id`
   - Ordered by `created_at DESC`
3. System applies pagination
4. System returns notification list

**Postconditions:**
- Notifications displayed

**Business Rules:**
- Only user's own notifications visible
- Pagination: 20 notifications per page

---

#### FR-NOTIF-1.3 Mark Notification as Read

**Description:** User marks notification as read.

**Actor:** Customer, Sales, Admin

**Main Flow:**
1. User clicks on notification
2. System updates notification:
   - `is_read = true`
   - `read_at = CURRENT_TIMESTAMP`
3. System returns success

**Postconditions:**
- Notification marked as read

---

#### FR-NOTIF-1.4 Get Unread Count

**Description:** System returns count of unread notifications for user.

**Actor:** Customer, Sales, Admin

**Main Flow:**
1. System queries `notifications` table:
   - `user_id = current_user.id`
   - `is_read = false`
2. System returns count

**Postconditions:**
- Unread count returned

---

### 7.2 Notification Types

**Customer Notifications:**
- `PAYMENT_APPROVED` - Payment approved, order processing
- `PAYMENT_REJECTED` - Payment rejected with reason
- `PAYMENT_RESUBMIT_REQUESTED` - Request to resubmit payment
- `ORDER_STATUS_UPDATED` - Order status changed
- `ORDER_DISPATCHED` - Order dispatched for delivery
- `ORDER_DELIVERED` - Order delivered

**Sales/Admin Notifications:**
- `NEW_ORDER` - New order placed
- `NEW_PAYMENT_SUBMITTED` - New payment submitted for review

---

## 8. Admin Dashboard

### 8.1 Dashboard Overview

#### FR-ADM-1.1 View Dashboard

**Description:** Admin/Sales views dashboard with key metrics.

**Actor:** Sales, Admin

**Preconditions:**
- User authenticated
- User has Sales or Admin role

**Main Flow:**
1. User navigates to Dashboard
2. System calculates metrics:
   - Orders today
   - Pending payments count
   - Orders by status (counts)
   - Revenue today (from approved payments)
3. System returns dashboard data

**Postconditions:**
- Dashboard displayed with metrics

---

### 8.2 Order Management (Admin/Sales)

#### FR-ADM-2.1 List All Orders

**Description:** Sales/Admin views list of all orders with filters.

**Actor:** Sales, Admin

**Preconditions:**
- User authenticated
- User has Sales or Admin role

**Main Flow:**
1. Sales/Admin navigates to Orders page
2. System queries `orders` table
3. System applies filters (if provided):
   - Status
   - Date range
   - Customer
   - Order number
4. System applies pagination
5. System returns order list

**Postconditions:**
- Order list displayed

**Business Rules:**
- All orders visible (not restricted to own orders)
- Pagination: 20 orders per page

---

#### FR-ADM-2.2 View Order Detail (Any Order)

**Description:** Sales/Admin views detailed information for any order.

**Actor:** Sales, Admin

**Preconditions:**
- Order exists

**Main Flow:**
1. Sales/Admin clicks on order
2. System queries order details:
   - Order information
   - Order items
   - Payment information
   - Status history
   - Customer information
3. System returns order detail

**Postconditions:**
- Order detail displayed

**Business Rules:**
- Sales/Admin can view any order (no ownership restriction)

---

### 8.3 Reporting

#### FR-ADM-3.1 Orders Report

**Description:** Admin views orders report with date range.

**Actor:** Admin

**Main Flow:**
1. Admin navigates to Reports > Orders
2. Admin selects date range
3. System queries orders in date range
4. System calculates:
   - Orders per day/week/month
   - Orders by status
   - Orders by delivery zone
5. System returns report data

**Postconditions:**
- Orders report displayed

---

#### FR-ADM-3.2 Revenue Report

**Description:** Admin views revenue report from approved payments.

**Actor:** Admin

**Main Flow:**
1. Admin navigates to Reports > Revenue
2. Admin selects date range
3. System queries approved payments in date range:
   - `payments.status = 'approved'`
   - Join with orders for amounts
4. System calculates:
   - Revenue per day/week/month
   - Revenue by payment method
   - Total revenue
5. System returns report data

**Postconditions:**
- Revenue report displayed

**Business Rules:**
- Only approved payments counted
- Revenue = order total from approved payments

---

#### FR-ADM-3.3 Top Products Report

**Description:** Admin views top selling products report.

**Actor:** Admin

**Main Flow:**
1. Admin navigates to Reports > Top Products
2. Admin selects date range
3. System queries `order_items` for delivered orders:
   - Join with orders where `status = 'DELIVERED'`
   - Group by product
   - Sum quantities
4. System orders by quantity sold DESC
5. System returns top products

**Postconditions:**
- Top products report displayed

---

#### FR-ADM-3.4 Unpaid Orders Aging Report

**Description:** Admin views report of unpaid orders by age.

**Actor:** Admin

**Main Flow:**
1. Admin navigates to Reports > Unpaid Orders
2. System queries orders:
   - Status in (`PENDING_PAYMENT`, `PAYMENT_SUBMITTED`, `PAYMENT_REJECTED`)
   - Calculate age (days since creation)
3. System groups by age ranges:
   - 0-1 days
   - 2-3 days
   - 4-7 days
   - 8+ days
4. System returns aging report

**Postconditions:**
- Unpaid orders aging report displayed

---

#### FR-ADM-3.5 Delivery Completion Rate

**Description:** Admin views delivery completion rate.

**Actor:** Admin

**Main Flow:**
1. Admin navigates to Reports > Delivery Completion
2. Admin selects date range
3. System queries orders in date range
4. System calculates:
   - Total orders
   - Delivered orders
   - Completion rate = (delivered / total) * 100
5. System returns completion rate

**Postconditions:**
- Delivery completion rate displayed

---

## 9. User Management (Admin)

### 9.1 User List

#### FR-ADM-4.1 List Users

**Description:** Admin views list of all users.

**Actor:** Admin

**Preconditions:**
- Admin authenticated

**Main Flow:**
1. Admin navigates to Users page
2. System queries `users` table
3. System applies filters (if provided):
   - Role
   - Search (name, phone, email)
4. System applies pagination
5. System returns user list

**Postconditions:**
- User list displayed

---

### 9.2 User Details

#### FR-ADM-4.2 View User Detail

**Description:** Admin views detailed user information.

**Actor:** Admin

**Preconditions:**
- User exists

**Main Flow:**
1. Admin clicks on user
2. System queries user details:
   - User information
   - Orders count
   - Recent orders
   - Account creation date
3. System returns user detail

**Postconditions:**
- User detail displayed

---

## 10. System Configuration

### 10.1 Stock Reservation Strategy

**Configuration Option:** Stock reservation timing

**Options:**
1. **On Order Placement:** Reserve stock when order created (`PENDING_PAYMENT`)
2. **On Payment Approval:** Reserve stock when payment approved (`PAID`)

**Default:** On Order Placement (recommended)

**Impact:**
- Affects when `product_variants.stock_qty` is decremented
- Affects stock availability display

---

### 10.2 OTP Configuration

**Configuration Options:**
- OTP expiration time (default: 5 minutes)
- OTP code length (default: 6 digits)
- Rate limiting thresholds
- OTP provider (dev mode, SMS gateway, etc.)

---

### 10.3 JWT Token Configuration

**Configuration Options:**
- Access token expiration (default: 15 minutes)
- Refresh token expiration (default: 7 days)
- Token rotation on refresh (optional)

---

## 11. Error Handling

### 11.1 Validation Errors

**Description:** System returns validation errors for invalid input.

**Response Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "phone",
        "message": "Invalid phone number format"
      }
    ]
  }
}
```

---

### 11.2 Business Rule Violations

**Description:** System returns errors when business rules are violated.

**Examples:**
- "Insufficient stock available"
- "Order cannot be cancelled in current status"
- "Invalid status transition"
- "Payment already submitted for this order"

---

### 11.3 Authentication Errors

**Description:** System returns authentication/authorization errors.

**Examples:**
- "Invalid OTP code"
- "OTP expired"
- "Unauthorized access"
- "Invalid refresh token"

---

## 12. Acceptance Criteria Summary

### 12.1 Customer Acceptance Criteria

✅ Customer can:
- Sign up/login with phone OTP
- Browse products (public, no auth required)
- View product details with variants and stock
- Place order for in-stock items
- See payment methods after ordering
- Upload payment screenshot
- Track order status with timeline
- View order history
- Cancel order (if eligible)
- Receive notifications for order updates

---

### 12.2 Admin Acceptance Criteria

✅ Admin can:
- Manage products (create, update, delete)
- Manage product variants and stock
- Manage categories
- Upload product images
- Configure payment methods
- Configure delivery zones with fees and ETAs
- Create Sales/Admin users
- Manage user roles
- View all orders
- View payment review queue
- View reports (orders, revenue, top products, etc.)

---

### 12.3 Sales Acceptance Criteria

✅ Sales can:
- View all orders
- View payment review queue
- Approve/reject/resubmit payment requests
- Update order statuses (PACKING → DISPATCHED → DELIVERED)
- Cancel orders with reason
- View order details and payment screenshots
- Receive notifications for new orders and payments

---

### 12.4 System Acceptance Criteria

✅ System:
- Validates all inputs
- Enforces business rules
- Maintains audit trail (status history)
- Handles stock reservation correctly
- Calculates delivery fees and ETAs
- Generates unique order numbers
- Stores payment screenshots securely
- Sends notifications for key events
- Supports multi-identity user accounts (phone, email, Telegram)
- Enforces role-based access control

---

## 13. Future Enhancements (Out of Scope for v1)

The following features are explicitly planned for future versions but not included in v1:

- Telegram Mini App UI packaging
- Telegram bot notifications
- Customer reorder in 1 click
- Discount codes / bundles
- Multi-branch inventory
- Courier assignment + tracking
- Basic accounting export (CSV)
- Account merging (manual by Admin)
- Fine-grained permissions system

---

**Document Status:** Draft v1.0  
**Last Updated:** Based on SRS v1.0, Architecture Design v1.0, Database Design v1.0  
**Next Review:** After implementation decisions are made

