# Implementation Plan - simpleCommerce Platform

**Version:** 1.0  
**Last Updated:** Based on Functional Requirements v1.0  
**Approach:** Phased implementation starting with core/basic features

---

## Overview

This document outlines the implementation plan for the simpleCommerce platform, organized into phases that prioritize basic and core features first. Each phase builds upon the previous one, ensuring a working system at each stage.

---

## Phase 1: Foundation & Core Infrastructure (Week 1-2)

**Goal:** Set up the foundational infrastructure and basic database schema to support all features.

### 1.1 Database Schema & Models
- [ ] Create all database models (Users, Products, Orders, Payments, etc.)
- [ ] Set up Alembic migrations
- [ ] Create initial migration with all tables
- [ ] Add database indexes for performance
- [ ] Set up database relationships and constraints

**Priority:** CRITICAL - Required for everything else

### 1.2 Core Configuration & Utilities
- [ ] Complete `app/core/config.py` with all environment variables
- [ ] Set up database connection and session management
- [ ] Configure JWT token generation and validation
- [ ] Set up MinIO/S3 client for file storage
- [ ] Create utility functions (password hashing, token generation, etc.)
- [ ] Set up error handling middleware
- [ ] Configure logging

**Priority:** CRITICAL - Required for everything else

### 1.3 Basic API Structure
- [ ] Set up API router structure (`/api/v1/`)
- [ ] Create base response schemas
- [ ] Set up authentication middleware
- [ ] Create health check endpoint
- [ ] Set up API documentation (OpenAPI/Swagger)

**Priority:** HIGH - Needed for API development

---

## Phase 2: Authentication & User Management (Week 2-3)

**Goal:** Enable users to authenticate and manage their accounts.

### 2.1 Phone OTP Authentication (Primary)
- [ ] **Request OTP Endpoint**
  - Validate phone number format
  - Generate 6-digit OTP
  - Store OTP with expiration (5 minutes)
  - Implement rate limiting (3 per phone/15min, 5 per IP/15min)
  - Send OTP via SMS (or dev mode logging)

- [ ] **Verify OTP & Login Endpoint**
  - Validate OTP code
  - Check expiration
  - Create user if doesn't exist (default role: customer)
  - Generate JWT access token (15 min) and refresh token (7 days)
  - Store refresh token in database
  - Return tokens to client

**Priority:** CRITICAL - Required for user access

### 2.2 Token Management
- [ ] **Refresh Token Endpoint**
  - Validate refresh token
  - Generate new access token
  - Optionally rotate refresh token

- [ ] **Logout Endpoint**
  - Revoke refresh token
  - Clear session

**Priority:** HIGH - Required for session management

### 2.3 User Profile (Basic)
- [ ] **Get Current User Endpoint**
  - Return authenticated user's profile

- [ ] **Update User Profile Endpoint**
  - Update name, email (optional)
  - Validate inputs

**Priority:** MEDIUM - Nice to have for user experience

---

## Phase 3: Product Catalog - Basic (Week 3-4)

**Goal:** Enable customers to browse products and admins to manage products.

### 3.1 Product Management (Admin)
- [ ] **Create Product Endpoint**
  - Validate product data
  - Generate slug from name
  - Create product record

- [ ] **List Products Endpoint (Admin)**
  - List all products with pagination
  - Filter by active/inactive
  - Search functionality

- [ ] **Get Product Detail Endpoint (Admin)**
  - Return full product information

- [ ] **Update Product Endpoint**
  - Update product fields
  - Validate changes

- [ ] **Delete Product Endpoint (Soft Delete)**
  - Set `deleted_at` timestamp
  - Set `is_active = false`

**Priority:** HIGH - Required for product management

### 3.2 Product Variant Management (Admin)
- [ ] **Create Variant Endpoint**
  - Validate variant data (label, price, stock)
  - Check label uniqueness per product
  - Check SKU uniqueness (if provided)
  - Create variant record

- [ ] **Update Variant Endpoint**
  - Update variant fields
  - Update stock quantity

- [ ] **List Variants Endpoint**
  - List variants for a product

**Priority:** HIGH - Required for product ordering

### 3.3 Customer Product Browsing (Public)
- [ ] **List Products Endpoint (Public)**
  - Show only active, non-deleted products
  - Show only products with active variants
  - Include price range (min/max from variants)
  - Include stock availability
  - Pagination (20 per page)
  - Filter by category (if implemented)
  - Search by name/description

- [ ] **Get Product Detail Endpoint (Public)**
  - Return product with all active variants
  - Include stock information per variant
  - Include product images (if implemented)

**Priority:** CRITICAL - Required for customer shopping

### 3.4 Product Images (Basic)
- [ ] **Upload Product Image Endpoint**
  - Validate file type (jpg/png)
  - Validate file size (max 5MB)
  - Upload to MinIO/S3
  - Create image record in database
  - Set sort order

- [ ] **List Product Images Endpoint**
  - Return images for a product

- [ ] **Delete Product Image Endpoint**
  - Remove from storage
  - Delete database record

**Priority:** MEDIUM - Enhances product browsing

---

## Phase 4: Order Management - Core (Week 4-6)

**Goal:** Enable customers to place orders and view their order history.

### 4.1 Order Placement
- [ ] **Create Order Endpoint**
  - Validate cart items (products exist, variants exist, stock available)
  - Validate delivery address and recipient info
  - Calculate subtotal (sum of line items)
  - Calculate delivery fee (from delivery zone)
  - Calculate total (subtotal + delivery fee)
  - Calculate expected delivery dates (from zone ETA)
  - Generate unique order number (`ORD-{YYYYMMDD}-{sequential}`)
  - Create order with status `PENDING_PAYMENT`
  - Create order items (with product/variant snapshots)
  - Create initial status history entry
  - **Stock Reservation:** Reserve stock if configured (decrement `stock_qty`)
  - Return order details with payment instructions

**Priority:** CRITICAL - Core business functionality

### 4.2 Order Tracking (Customer)
- [ ] **List My Orders Endpoint**
  - Return orders for authenticated customer
  - Pagination (10 per page)
  - Order by `created_at DESC`
  - Include order number, date, status, total

- [ ] **Get Order Detail Endpoint**
  - Return full order information
  - Include order items (with snapshots)
  - Include payment information (if submitted)
  - Include status history timeline
  - Verify order ownership

**Priority:** CRITICAL - Required for customer experience

### 4.3 Order Cancellation (Customer)
- [ ] **Cancel Order Endpoint**
  - Validate order belongs to customer
  - Validate order status is `PENDING_PAYMENT`
  - Validate no payment approved
  - Update order status to `CANCELLED`
  - Set `cancelled_at` timestamp
  - Set cancellation reason
  - Log status change
  - Release stock if reserved (increment `stock_qty`)
  - Create notification

**Priority:** HIGH - Important for customer control

---

## Phase 5: Payment Workflow - Core (Week 6-7)

**Goal:** Enable payment submission and review workflow.

### 5.1 Payment Method Management (Admin)
- [ ] **Create Payment Method Endpoint**
  - Validate payment method data
  - Create payment method record

- [ ] **List Payment Methods Endpoint (Public)**
  - Return active payment methods
  - Ordered by `sort_order`
  - Include account details and instructions

- [ ] **Update Payment Method Endpoint**
  - Update payment method fields

**Priority:** HIGH - Required for payment workflow

### 5.2 Payment Submission (Customer)
- [ ] **Upload Payment Screenshot Endpoint**
  - Validate file type (jpg/png) and size (max 5MB)
  - Validate order status allows payment submission
  - Upload screenshot to MinIO/S3
  - Create payment record with status `submitted`
  - Update order status to `PAYMENT_SUBMITTED`
  - Log status change
  - Create notification for Sales/Admin

**Priority:** CRITICAL - Core payment functionality

### 5.3 Payment Review Queue (Sales/Admin)
- [ ] **List Payment Queue Endpoint**
  - Return payments with status `submitted`
  - Ordered by `created_at ASC` (oldest first)
  - Include order and customer information
  - Filter by date range, amount, method, customer

- [ ] **Get Payment Detail Endpoint**
  - Return payment with screenshot URL
  - Include order details and customer info

**Priority:** CRITICAL - Required for payment processing

### 5.4 Payment Review Actions (Sales/Admin)
- [ ] **Approve Payment Endpoint**
  - Validate payment status is `submitted`
  - Update payment status to `approved`
  - Set `reviewed_by` and `reviewed_at`
  - Update order status to `PAID`
  - Log status change
  - **Stock Reservation:** Reserve stock if configured for payment approval
  - Create notification for customer

- [ ] **Reject Payment Endpoint**
  - Validate payment status is `submitted`
  - Require rejection reason
  - Update payment status to `rejected`
  - Update order status to `PAYMENT_REJECTED`
  - Log status change
  - Create notification for customer with reason

- [ ] **Request Payment Resubmission Endpoint**
  - Update payment status to `resubmit_requested`
  - Update order status to `PAYMENT_RESUBMIT_REQUESTED`
  - Log status change
  - Create notification for customer

**Priority:** CRITICAL - Core payment processing

---

## Phase 6: Order Fulfillment - Basic (Week 7-8)

**Goal:** Enable Sales/Admin to manage order fulfillment.

### 6.1 Order Status Updates (Sales/Admin)
- [ ] **Update Order Status Endpoint**
  - Validate status transition (state machine)
  - Update order status
  - Log status change with actor
  - Create notification for customer
  - Support transitions:
    - `PAID` → `PACKING`
    - `PACKING` → `DISPATCHED`
    - `DISPATCHED` → `DELIVERED`

- [ ] **Mark as Delivered Endpoint**
  - Update status to `DELIVERED`
  - Optionally upload delivery proof image
  - Log status change
  - Create notification

**Priority:** HIGH - Required for order fulfillment

### 6.2 Delivery Zone Management (Admin)
- [ ] **Create Delivery Zone Endpoint**
  - Validate zone data
  - Create zone record

- [ ] **List Delivery Zones Endpoint**
  - Return active zones
  - Include fee and ETA information

- [ ] **Update Delivery Zone Endpoint**
  - Update zone fields

- [ ] **Calculate Delivery Fee Endpoint**
  - Calculate fee and ETA based on zone
  - Return expected delivery dates

**Priority:** MEDIUM - Required for order placement calculations

### 6.3 Order Management (Sales/Admin)
- [ ] **List All Orders Endpoint**
  - Return all orders (not restricted to customer)
  - Filter by status, date range, customer, order number
  - Pagination (20 per page)

- [ ] **Get Order Detail Endpoint (Any Order)**
  - Return full order information
  - No ownership restriction for Sales/Admin

- [ ] **Cancel Order Endpoint (Sales/Admin)**
  - Cancel any order (except DELIVERED)
  - Require cancellation reason
  - Optionally restock items
  - Create notification

**Priority:** HIGH - Required for admin operations

---

## Phase 7: Notifications - Basic (Week 8)

**Goal:** Enable in-app notifications for key events.

### 7.1 Notification System
- [x] **Create Notification Service**
  - Create notification records in database
  - Support notification types (enum)

- [x] **List Notifications Endpoint**
  - Return notifications for authenticated user
  - Pagination (20 per page)
  - Order by `created_at DESC`

- [x] **Mark Notification as Read Endpoint**
  - Update `is_read = true`
  - Set `read_at` timestamp

- [x] **Get Unread Count Endpoint**
  - Return count of unread notifications

**Priority:** MEDIUM - Enhances user experience

### 7.2 Notification Triggers
- [x] Integrate notification creation for:
  - Payment approved
  - Payment rejected
  - Payment resubmission requested
  - Order status updated
  - Order dispatched
  - Order delivered
  - New order (for Sales/Admin)
  - New payment submitted (for Sales/Admin)

**Priority:** MEDIUM - Completes notification system

---

## Phase 8: Admin Dashboard - Basic (Week 9)

**Goal:** Provide admin dashboard with key metrics.

### 8.1 Dashboard Overview
- [x] **Dashboard Endpoint**
  - Orders today (count)
  - Pending payments count
  - Orders by status (counts)
  - Revenue today (from approved payments)
  - Recent orders (last 10)

**Priority:** MEDIUM - Useful for admin operations

### 8.2 User Management (Admin)
- [x] **List Users Endpoint**
  - Return all users
  - Filter by role, search by name/phone/email
  - Pagination

- [x] **Get User Detail Endpoint**
  - Return user information
  - Include orders count and recent orders

- [x] **Create Sales/Admin User Endpoint**
  - Create user with specified role
  - Send OTP for initial verification

- [x] **Update User Role Endpoint**
  - Update user role
  - Log role change (audit trail)
  - Validate (cannot change own role, cannot remove last admin)

**Priority:** MEDIUM - Required for user management

---

## Phase 9: Frontend - Core Pages (Week 10-12)

**Goal:** Build essential frontend pages for customers and admins.

### 9.1 Frontend Foundation
- [x] Set up theme system (colors, typography, spacing)
- [x] Create base layout components
- [x] Set up routing structure
- [x] Create API service layer
- [x] Set up authentication context/state
- [x] Create protected route components
- [x] Set up error handling and loading states

**Priority:** CRITICAL - Required for frontend

### 9.2 Authentication Pages
- [x] **Login Page**
  - Phone number input
  - OTP request flow
  - OTP verification flow
  - Token storage

- [x] **Protected Route Wrapper**
  - Check authentication
  - Redirect to login if not authenticated

**Priority:** CRITICAL - Required for user access

### 9.3 Customer Storefront
- [x] **Product List Page**
  - Display products with images
  - Show price range and stock availability
  - Search and filter functionality
  - Pagination

- [x] **Product Detail Page**
  - Display product information
  - Show all variants with prices and stock
  - Add to cart functionality
  - Image gallery

- [x] **Shopping Cart Page**
  - Display cart items
  - Update quantities
  - Remove items
  - Client-side cart management (localStorage)

- [x] **Checkout Page**
  - Delivery address form
  - Recipient information
  - Delivery zone selection
  - Order summary
  - Place order

- [x] **Payment Upload Page**
  - Display payment methods
  - Display order details
  - Upload payment screenshot
  - Enter payment details (optional)

- [x] **My Orders Page**
  - List customer orders
  - Order status display
  - Link to order detail

- [x] **Order Detail Page**
  - Display order information
  - Order items list
  - Payment information
  - Status timeline/history

**Priority:** CRITICAL - Core customer experience

### 9.4 Admin Dashboard
- [x] **Dashboard Page**
  - Display key metrics
  - Recent orders
  - Quick actions

- [x] **Products Management Page**
  - List products
  - Create product form
  - Edit product form
  - Delete product
  - Manage variants
  - Upload images

- [x] **Orders Management Page**
  - List all orders
  - Filter and search
  - Order detail view
  - Update order status
  - Cancel order

- [x] **Payment Queue Page**
  - List pending payments
  - View payment with screenshot
  - Approve/reject/resubmit actions

- [x] **Payment Methods Page**
  - List payment methods
  - Create/edit payment methods

- [x] **Delivery Zones Page**
  - List delivery zones
  - Create/edit zones

- [x] **Users Management Page** (Admin only)
  - List users
  - Create Sales/Admin users
  - Update user roles

**Priority:** HIGH - Required for admin operations

---

## Phase 10: Category Management (Week 13)

**Goal:** Add category support for product organization.

### 10.1 Category Management (Admin)
- [ ] **Create Category Endpoint**
  - Validate category data
  - Generate slug
  - Support parent category (hierarchy)

- [ ] **List Categories Endpoint**
  - Return all categories
  - Support hierarchy display

- [ ] **Update Category Endpoint**
  - Update category fields

- [ ] **Delete Category Endpoint**
  - Soft delete category

**Priority:** LOW - Nice to have for organization

### 10.2 Product-Category Association
- [ ] Update product creation/update to support categories
- [ ] Update product list to filter by category

**Priority:** LOW - Enhances product browsing

---

## Phase 11: Email Authentication (Week 14)

**Goal:** Add email as alternative authentication method.

### 11.1 Email OTP Authentication
- [ ] **Request Email OTP Endpoint**
  - Generate OTP
  - Send via email (or dev mode)
  - Store with expiration

- [ ] **Verify Email OTP Endpoint**
  - Validate OTP
  - Create/update user
  - Issue tokens

**Priority:** LOW - Backup authentication method

---

## Phase 12: Reporting - Basic (Week 15)

**Goal:** Add basic reporting functionality.

### 12.1 Reports (Admin)
- [ ] **Orders Report Endpoint**
  - Orders per day/week/month
  - Orders by status
  - Orders by delivery zone

- [ ] **Revenue Report Endpoint**
  - Revenue per day/week/month
  - Revenue by payment method
  - Total revenue

- [ ] **Top Products Report Endpoint**
  - Products by quantity sold
  - Date range filter

**Priority:** LOW - Useful for business insights

---

## Implementation Notes

### Dependencies Between Phases
- **Phase 1** must be completed before all others
- **Phase 2** (Authentication) is required for customer and admin features
- **Phase 3** (Products) is required before **Phase 4** (Orders)
- **Phase 4** (Orders) is required before **Phase 5** (Payments)
- **Phase 5** (Payments) is required before **Phase 6** (Fulfillment)
- **Phase 9** (Frontend) can be developed in parallel with backend phases, but requires backend APIs

### Testing Strategy
- Unit tests for services and utilities
- Integration tests for API endpoints
- End-to-end tests for critical user flows (future)

### Deployment Considerations
- Each phase should be deployable independently
- Database migrations must be backward compatible where possible
- Feature flags for incomplete features (if needed)

---

## Priority Summary

### CRITICAL (Must Have for MVP)
1. Phase 1: Foundation & Core Infrastructure
2. Phase 2: Authentication & User Management (Phone OTP)
3. Phase 3: Product Catalog - Basic
4. Phase 4: Order Management - Core
5. Phase 5: Payment Workflow - Core
6. Phase 9: Frontend - Core Pages

### HIGH (Important for MVP)
1. Phase 6: Order Fulfillment - Basic
2. Phase 2: Token Management
3. Phase 3: Product Variant Management

### MEDIUM (Enhances MVP)
1. Phase 7: Notifications - Basic
2. Phase 8: Admin Dashboard - Basic
3. Phase 3: Product Images
4. Phase 6: Delivery Zone Management

### LOW (Nice to Have)
1. Phase 10: Category Management
2. Phase 11: Email Authentication
3. Phase 12: Reporting - Basic

---

## Estimated Timeline

- **Weeks 1-2:** Phase 1 (Foundation)
- **Weeks 2-3:** Phase 2 (Authentication)
- **Weeks 3-4:** Phase 3 (Products)
- **Weeks 4-6:** Phase 4 (Orders)
- **Weeks 6-7:** Phase 5 (Payments)
- **Weeks 7-8:** Phase 6 (Fulfillment)
- **Week 8:** Phase 7 (Notifications)
- **Week 9:** Phase 8 (Admin Dashboard)
- **Weeks 10-12:** Phase 9 (Frontend)
- **Week 13:** Phase 10 (Categories)
- **Week 14:** Phase 11 (Email Auth)
- **Week 15:** Phase 12 (Reporting)

**Total Estimated Time:** 15 weeks for full implementation

**MVP Timeline (Critical + High Priority):** ~10-11 weeks

---

## Next Steps

1. **Phase 10 – Category Management:** Backend and UI for categories (optional; frontend already has AdminCategoriesPage if backend is ready).
2. Set up CI/CD pipeline (if not already done).
3. Set up testing framework.

---

**Document Status:** Draft v1.0  
**Last Updated:** Phase 7.2 Notification Triggers completed; MVP core phases finalized  
**Next Review:** As needed for Phase 10 or reporting

