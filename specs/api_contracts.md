# API Contracts Document

**Project Name:** simpleCommerce Commerce & Order Operations Platform  
**Version:** 1.0  
**API Version:** v1  
**Based on:** Software Requirements Specification v1.0, Architecture Design v1.0, Database Design v1.0, Functional Requirements v1.0

---

## 1. API Overview

### 1.1 Base URL

```
Production: https://api.simpleCommerce.com/api/v1
Development: http://localhost:8000/api/v1
```

### 1.2 API Versioning

- **Strategy:** URL path versioning
- **Format:** `/api/v1/`
- **Version Header:** Optional `X-API-Version: v1` header

### 1.3 Content Type

- **Request:** `application/json` (except file uploads: `multipart/form-data`)
- **Response:** `application/json`

### 1.4 Authentication

- **Method:** JWT Bearer Token
- **Header:** `Authorization: Bearer <access_token>`
- **Alternative:** HTTP-only cookies (recommended for web)
- **Token Types:**
  - Access Token: Short-lived (15 minutes)
  - Refresh Token: Long-lived (7 days)

---

## 2. Standard Response Formats

### 2.1 Success Response

**Single Resource:**
```json
{
  "data": {
    // Resource data
  }
}
```

**List Resource:**
```json
{
  "data": [
    // Array of resources
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### 2.2 Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "field_name",
        "message": "Field-specific error message"
      }
    ]
  }
}
```

### 2.3 HTTP Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error, invalid input
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity` - Business rule violation
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## 3. Authentication Endpoints

### 3.1 Request Phone OTP

**Endpoint:** `POST /api/v1/auth/otp/request`

**Description:** Request OTP code via phone number.

**Authentication:** Not required

**Request Body:**
```json
{
  "phone": "+251912345678"
}
```

**Request Schema:**
- `phone` (string, required): Phone number in E.164 format

**Response:** `200 OK`
```json
{
  "data": {
    "message": "OTP sent successfully",
    "expires_in": 300
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid phone format
- `429 Too Many Requests`: Rate limit exceeded

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{"phone": "+251912345678"}'
```

---

### 3.2 Verify Phone OTP

**Endpoint:** `POST /api/v1/auth/otp/verify`

**Description:** Verify OTP code and receive JWT tokens.

**Authentication:** Not required

**Request Body:**
```json
{
  "phone": "+251912345678",
  "code": "123456"
}
```

**Request Schema:**
- `phone` (string, required): Phone number
- `code` (string, required): 6-digit OTP code

**Response:** `200 OK`
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "phone": "+251912345678",
      "phone_verified": true,
      "role": "customer",
      "first_name": null,
      "last_name": null
    }
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid OTP code
- `422 Unprocessable Entity`: OTP expired or already used

---

### 3.3 Request Email OTP/Magic Link

**Endpoint:** `POST /api/v1/auth/email/request`

**Description:** Request email-based authentication (OTP or magic link).

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Request Schema:**
- `email` (string, required, format: email): Email address

**Response:** `200 OK`
```json
{
  "data": {
    "message": "OTP sent to email",
    "expires_in": 300
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email format
- `429 Too Many Requests`: Rate limit exceeded

---

### 3.4 Verify Email OTP/Magic Link

**Endpoint:** `POST /api/v1/auth/email/verify`

**Description:** Verify email OTP/magic link and receive JWT tokens.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response:** `200 OK` (Same structure as phone OTP verify)

---

### 3.5 Verify Telegram Authentication

**Endpoint:** `POST /api/v1/auth/telegram/verify`

**Description:** Verify Telegram WebApp initData and link/create account.

**Authentication:** Not required

**Request Body:**
```json
{
  "init_data": "query_id=AAHdF6IQAAAAAN0XohDhrOr6&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladislav%22%2C%22last_name%22%3A%22Kibenko%22%2C%22username%22%3A%22vdkfrost%22%2C%22language_code%22%3A%22ru%22%7D&auth_date=1662771648&hash=c501b71e775f74ce10e377dea85a7ea24ecd640b5ea86f65d52c587f8ed368e00"
}
```

**Request Schema:**
- `init_data` (string, required): Telegram WebApp initData string

**Response:** `200 OK`
```json
{
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "telegram_user_id": 279058397,
      "telegram_username": "vdkfrost",
      "first_name": "Vladislav",
      "last_name": "Kibenko",
      "phone_verified": false,
      "requires_phone_verification": true,
      "role": "customer"
    }
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid initData format
- `422 Unprocessable Entity`: Invalid signature or expired

---

### 3.6 Refresh Access Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Description:** Refresh expired access token using refresh token.

**Authentication:** Not required (uses refresh token)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Request Schema:**
- `refresh_token` (string, required): Refresh token

**Response:** `200 OK`
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

---

### 3.7 Logout

**Endpoint:** `POST /api/v1/auth/logout`

**Description:** Invalidate refresh token and logout user.

**Authentication:** Required

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## 4. Product Endpoints

### 4.1 List Products

**Endpoint:** `GET /api/v1/products`

**Description:** List products with filtering and pagination (public endpoint).

**Authentication:** Not required

**Query Parameters:**
- `page` (integer, optional, default: 1): Page number
- `per_page` (integer, optional, default: 20, max: 100): Items per page
- `category_id` (integer, optional): Filter by category
- `search` (string, optional): Search in name and description
- `min_price` (decimal, optional): Minimum price filter
- `max_price` (decimal, optional): Maximum price filter
- `in_stock_only` (boolean, optional, default: false): Show only in-stock products
- `featured` (boolean, optional): Show only featured products

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "name": "Ethiopian Coffee Beans",
      "slug": "ethiopian-coffee-beans",
      "description": "Premium Ethiopian coffee beans",
      "category": {
        "id": 1,
        "name": "Coffee",
        "slug": "coffee"
      },
      "images": [
        {
          "id": 1,
          "url": "https://storage.example.com/products/1/image1.jpg",
          "alt_text": "Coffee beans",
          "sort_order": 0
        }
      ],
      "variants": [
        {
          "id": 1,
          "label": "250g",
          "price": "150.00",
          "stock_qty": 50,
          "is_active": true
        },
        {
          "id": 2,
          "label": "1kg",
          "price": "550.00",
          "stock_qty": 20,
          "is_active": true
        }
      ],
      "price_range": {
        "min": "150.00",
        "max": "550.00"
      },
      "in_stock": true,
      "is_featured": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

---

### 4.2 Get Product Detail

**Endpoint:** `GET /api/v1/products/{id}`

**Description:** Get detailed product information (public endpoint).

**Authentication:** Not required

**Path Parameters:**
- `id` (integer, required): Product ID

**Response:** `200 OK`
```json
{
  "data": {
    "id": 1,
    "name": "Ethiopian Coffee Beans",
    "slug": "ethiopian-coffee-beans",
    "description": "Premium Ethiopian coffee beans sourced from Yirgacheffe region.",
    "category": {
      "id": 1,
      "name": "Coffee",
      "slug": "coffee"
    },
    "tags": ["organic", "premium", "ethiopian"],
    "images": [
      {
        "id": 1,
        "url": "https://storage.example.com/products/1/image1.jpg",
        "alt_text": "Coffee beans",
        "sort_order": 0
      }
    ],
    "variants": [
      {
        "id": 1,
        "label": "250g",
        "price": "150.00",
        "stock_qty": 50,
        "sku": "COFFEE-250G",
        "is_active": true
      },
      {
        "id": 2,
        "label": "1kg",
        "price": "550.00",
        "stock_qty": 20,
        "sku": "COFFEE-1KG",
        "is_active": true
      }
    ],
    "is_featured": true,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
}
```

**Error Responses:**
- `404 Not Found`: Product not found or inactive

---

## 5. Order Endpoints

### 5.1 Create Order (Checkout)

**Endpoint:** `POST /api/v1/cart/checkout`

**Description:** Create order from cart items.

**Authentication:** Required (Customer role)

**Request Body:**
```json
{
  "items": [
    {
      "product_id": 1,
      "variant_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "variant_id": 3,
      "quantity": 1
    }
  ],
  "delivery_address": "123 Main Street, Addis Ababa",
  "recipient_name": "John Doe",
  "recipient_phone": "+251912345678",
  "delivery_instructions": "Ring doorbell twice",
  "delivery_zone_id": 1
}
```

**Request Schema:**
- `items` (array, required): Cart items
  - `product_id` (integer, required): Product ID
  - `variant_id` (integer, optional): Variant ID (required if product has variants)
  - `quantity` (integer, required, min: 1): Quantity
- `delivery_address` (string, required): Full delivery address
- `recipient_name` (string, required): Recipient name
- `recipient_phone` (string, required): Recipient phone
- `delivery_instructions` (string, optional): Delivery instructions
- `delivery_zone_id` (integer, required): Delivery zone ID

**Response:** `201 Created`
```json
{
  "data": {
    "id": 123,
    "order_number": "ORD-20240115-0001",
    "status": "PENDING_PAYMENT",
    "subtotal": "300.00",
    "delivery_fee": "50.00",
    "total": "350.00",
    "delivery_address": "123 Main Street, Addis Ababa",
    "recipient_name": "John Doe",
    "recipient_phone": "+251912345678",
    "delivery_instructions": "Ring doorbell twice",
    "expected_delivery_from": "2024-01-16",
    "expected_delivery_to": "2024-01-17",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "variant_id": 1,
        "product_name": "Ethiopian Coffee Beans",
        "variant_label": "250g",
        "quantity": 2,
        "unit_price": "150.00",
        "line_total": "300.00"
      }
    ],
    "payment_methods": [
      {
        "id": 1,
        "type": "BANK_TRANSFER",
        "name": "CBE Bank",
        "account_identifier": "1234567890",
        "account_holder": "simpleCommerce Foods",
        "instructions": "Transfer to account number above"
      }
    ],
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Validation error
- `422 Unprocessable Entity`: Insufficient stock, invalid variant, etc.

---

### 5.2 List My Orders

**Endpoint:** `GET /api/v1/orders/my`

**Description:** List customer's own orders.

**Authentication:** Required (Customer role)

**Query Parameters:**
- `page` (integer, optional, default: 1): Page number
- `per_page` (integer, optional, default: 10, max: 50): Items per page
- `status` (string, optional): Filter by status

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 123,
      "order_number": "ORD-20240115-0001",
      "status": "PAID",
      "total": "350.00",
      "delivery_address": "123 Main Street, Addis Ababa",
      "expected_delivery_from": "2024-01-16",
      "expected_delivery_to": "2024-01-17",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

---

### 5.3 Get Order Detail

**Endpoint:** `GET /api/v1/orders/{id}`

**Description:** Get detailed order information (customer can only view own orders).

**Authentication:** Required (Customer role)

**Path Parameters:**
- `id` (integer, required): Order ID

**Response:** `200 OK`
```json
{
  "data": {
    "id": 123,
    "order_number": "ORD-20240115-0001",
    "status": "PAID",
    "subtotal": "300.00",
    "delivery_fee": "50.00",
    "total": "350.00",
    "delivery_address": "123 Main Street, Addis Ababa",
    "recipient_name": "John Doe",
    "recipient_phone": "+251912345678",
    "delivery_instructions": "Ring doorbell twice",
    "expected_delivery_from": "2024-01-16",
    "expected_delivery_to": "2024-01-17",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "variant_id": 1,
        "product_name": "Ethiopian Coffee Beans",
        "variant_label": "250g",
        "quantity": 2,
        "unit_price": "150.00",
        "line_total": "300.00"
      }
    ],
    "payment": {
      "id": 45,
      "status": "approved",
      "method": {
        "name": "CBE Bank",
        "type": "BANK_TRANSFER"
      },
      "screenshot_url": "https://storage.example.com/payments/45/screenshot.jpg",
      "reviewed_at": "2024-01-15T11:00:00Z"
    },
    "status_history": [
      {
        "id": 1,
        "old_status": null,
        "new_status": "PENDING_PAYMENT",
        "created_at": "2024-01-15T10:00:00Z"
      },
      {
        "id": 2,
        "old_status": "PENDING_PAYMENT",
        "new_status": "PAYMENT_SUBMITTED",
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": 3,
        "old_status": "PAYMENT_SUBMITTED",
        "new_status": "PAID",
        "actor": {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "name": "Sales User"
        },
        "created_at": "2024-01-15T11:00:00Z"
      }
    ],
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Error Responses:**
- `403 Forbidden`: Order does not belong to customer
- `404 Not Found`: Order not found

---

### 5.4 Upload Payment Screenshot

**Endpoint:** `POST /api/v1/orders/{id}/payment`

**Description:** Upload payment screenshot and submit payment information.

**Authentication:** Required (Customer role)

**Path Parameters:**
- `id` (integer, required): Order ID

**Request:** `multipart/form-data`
- `method_id` (integer, required): Payment method ID
- `screenshot` (file, required): Payment screenshot (jpg/png, max 5MB)
- `amount_declared` (decimal, optional): Amount declared by customer
- `reference_text` (string, optional): Transaction reference
- `paid_at` (datetime, optional): Payment date/time

**Response:** `201 Created`
```json
{
  "data": {
    "id": 45,
    "order_id": 123,
    "status": "submitted",
    "method": {
      "id": 1,
      "name": "CBE Bank",
      "type": "BANK_TRANSFER"
    },
    "screenshot_url": "https://storage.example.com/payments/45/screenshot.jpg",
    "amount_declared": "350.00",
    "reference_text": "TXN123456",
    "paid_at": "2024-01-15T10:25:00Z",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid file type or size
- `403 Forbidden`: Order does not belong to customer
- `422 Unprocessable Entity`: Order status does not allow payment submission

---

### 5.5 Cancel Order

**Endpoint:** `POST /api/v1/orders/{id}/cancel`

**Description:** Cancel order (customer can only cancel in PENDING_PAYMENT status).

**Authentication:** Required (Customer role)

**Path Parameters:**
- `id` (integer, required): Order ID

**Request Body:**
```json
{
  "reason": "Changed my mind"
}
```

**Request Schema:**
- `reason` (string, optional): Cancellation reason

**Response:** `200 OK`
```json
{
  "data": {
    "id": 123,
    "order_number": "ORD-20240115-0001",
    "status": "CANCELLED",
    "cancelled_at": "2024-01-15T11:00:00Z",
    "cancellation_reason": "Changed my mind"
  }
}
```

**Error Responses:**
- `403 Forbidden`: Order does not belong to customer
- `422 Unprocessable Entity`: Order cannot be cancelled in current status

---

## 6. Admin/Sales Order Endpoints

### 6.1 List All Orders

**Endpoint:** `GET /api/v1/admin/orders`

**Description:** List all orders with filters (Sales/Admin only).

**Authentication:** Required (Sales or Admin role)

**Query Parameters:**
- `page` (integer, optional, default: 1): Page number
- `per_page` (integer, optional, default: 20, max: 100): Items per page
- `status` (string, optional): Filter by status
- `date_from` (date, optional): Filter orders from date
- `date_to` (date, optional): Filter orders to date
- `customer_id` (uuid, optional): Filter by customer
- `order_number` (string, optional): Search by order number

**Response:** `200 OK` (Same structure as customer orders list, but includes customer information)

```json
{
  "data": [
    {
      "id": 123,
      "order_number": "ORD-20240115-0001",
      "status": "PAID",
      "total": "350.00",
      "customer": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "phone": "+251912345678",
        "name": "John Doe"
      },
      "delivery_address": "123 Main Street, Addis Ababa",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "total_pages": 8
    }
  }
}
```

---

### 6.2 Get Order Detail (Any Order)

**Endpoint:** `GET /api/v1/admin/orders/{id}`

**Description:** Get detailed order information (Sales/Admin can view any order).

**Authentication:** Required (Sales or Admin role)

**Path Parameters:**
- `id` (integer, required): Order ID

**Response:** `200 OK` (Same structure as customer order detail, but includes full customer information)

---

### 6.3 Update Order Status

**Endpoint:** `POST /api/v1/admin/orders/{id}/status`

**Description:** Update order status (Sales/Admin only).

**Authentication:** Required (Sales or Admin role)

**Path Parameters:**
- `id` (integer, required): Order ID

**Request Body:**
```json
{
  "status": "PACKING",
  "note": "Order being prepared"
}
```

**Request Schema:**
- `status` (string, required): New status (must be valid transition)
- `note` (string, optional): Status change note

**Response:** `200 OK`
```json
{
  "data": {
    "id": 123,
    "order_number": "ORD-20240115-0001",
    "status": "PACKING",
    "status_history": [
      {
        "id": 4,
        "old_status": "PAID",
        "new_status": "PACKING",
        "actor": {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "name": "Sales User"
        },
        "note": "Order being prepared",
        "created_at": "2024-01-15T12:00:00Z"
      }
    ]
  }
}
```

**Error Responses:**
- `422 Unprocessable Entity`: Invalid status transition

---

## 7. Payment Review Endpoints

### 7.1 Get Payment Queue

**Endpoint:** `GET /api/v1/admin/payments/queue`

**Description:** Get list of payments awaiting review (Sales/Admin only).

**Authentication:** Required (Sales or Admin role)

**Query Parameters:**
- `page` (integer, optional, default: 1): Page number
- `per_page` (integer, optional, default: 20, max: 100): Items per page
- `date_from` (date, optional): Filter from date
- `date_to` (date, optional): Filter to date
- `method_id` (integer, optional): Filter by payment method
- `customer_id` (uuid, optional): Filter by customer
- `min_amount` (decimal, optional): Minimum amount
- `max_amount` (decimal, optional): Maximum amount

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 45,
      "order": {
        "id": 123,
        "order_number": "ORD-20240115-0001",
        "total": "350.00",
        "status": "PAYMENT_SUBMITTED"
      },
      "customer": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "phone": "+251912345678",
        "name": "John Doe"
      },
      "method": {
        "id": 1,
        "name": "CBE Bank",
        "type": "BANK_TRANSFER"
      },
      "amount_declared": "350.00",
      "reference_text": "TXN123456",
      "screenshot_url": "https://storage.example.com/payments/45/screenshot.jpg",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 25,
      "total_pages": 2
    }
  }
}
```

---

### 7.2 Approve Payment

**Endpoint:** `POST /api/v1/admin/payments/{id}/approve`

**Description:** Approve a payment submission (Sales/Admin only).

**Authentication:** Required (Sales or Admin role)

**Path Parameters:**
- `id` (integer, required): Payment ID

**Request Body:**
```json
{
  "note": "Payment verified, amount matches"
}
```

**Request Schema:**
- `note` (string, optional): Review note

**Response:** `200 OK`
```json
{
  "data": {
    "id": 45,
    "status": "approved",
    "reviewed_by": {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Sales User"
    },
    "reviewed_at": "2024-01-15T11:00:00Z",
    "review_note": "Payment verified, amount matches",
    "order": {
      "id": 123,
      "status": "PAID"
    }
  }
}
```

**Error Responses:**
- `422 Unprocessable Entity`: Payment cannot be approved (wrong status)

---

### 7.3 Reject Payment

**Endpoint:** `POST /api/v1/admin/payments/{id}/reject`

**Description:** Reject a payment submission with reason (Sales/Admin only).

**Authentication:** Required (Sales or Admin role)

**Path Parameters:**
- `id` (integer, required): Payment ID

**Request Body:**
```json
{
  "reason": "Screenshot unclear, amount does not match"
}
```

**Request Schema:**
- `reason` (string, required): Rejection reason

**Response:** `200 OK` (Similar structure to approve, with status "rejected")

---

### 7.4 Request Payment Resubmission

**Endpoint:** `POST /api/v1/admin/payments/{id}/resubmit_request`

**Description:** Request customer to resubmit payment (Sales/Admin only).

**Authentication:** Required (Sales or Admin role)

**Path Parameters:**
- `id` (integer, required): Payment ID

**Request Body:**
```json
{
  "note": "Please provide clearer screenshot"
}
```

**Request Schema:**
- `note` (string, optional): Resubmission request note

**Response:** `200 OK` (Similar structure, with status "resubmit_requested")

---

## 8. Admin Configuration Endpoints

### 8.1 Product Management

#### 8.1.1 Create Product

**Endpoint:** `POST /api/v1/admin/products`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "name": "Ethiopian Coffee Beans",
  "description": "Premium Ethiopian coffee beans",
  "category_id": 1,
  "is_featured": true,
  "is_active": true
}
```

**Response:** `201 Created`

---

#### 8.1.2 Update Product

**Endpoint:** `PUT /api/v1/admin/products/{id}`

**Authentication:** Required (Admin role)

**Path Parameters:**
- `id` (integer, required): Product ID

**Request Body:** (Same as create, all fields optional)

**Response:** `200 OK`

---

#### 8.1.3 Delete Product

**Endpoint:** `DELETE /api/v1/admin/products/{id}`

**Authentication:** Required (Admin role)

**Path Parameters:**
- `id` (integer, required): Product ID

**Response:** `204 No Content`

---

#### 8.1.4 Upload Product Images

**Endpoint:** `POST /api/v1/admin/products/{id}/images`

**Authentication:** Required (Admin role)

**Path Parameters:**
- `id` (integer, required): Product ID

**Request:** `multipart/form-data`
- `images` (file[], required): Image files (jpg/png, max 5MB each)
- `alt_text` (string[], optional): Alt text for each image

**Response:** `201 Created`

---

### 8.2 Product Variant Management

#### 8.2.1 Create Variant

**Endpoint:** `POST /api/v1/admin/products/{product_id}/variants`

**Authentication:** Required (Admin role)

**Path Parameters:**
- `product_id` (integer, required): Product ID

**Request Body:**
```json
{
  "label": "250g",
  "price": "150.00",
  "stock_qty": 50,
  "sku": "COFFEE-250G",
  "is_active": true
}
```

**Response:** `201 Created`

---

#### 8.2.2 Update Variant Stock

**Endpoint:** `PATCH /api/v1/admin/variants/{id}/stock`

**Authentication:** Required (Admin role)

**Path Parameters:**
- `id` (integer, required): Variant ID

**Request Body:**
```json
{
  "stock_qty": 75
}
```

**Response:** `200 OK`

---

### 8.3 Category Management

#### 8.3.1 List Categories

**Endpoint:** `GET /api/v1/admin/categories`

**Authentication:** Required (Admin role)

**Response:** `200 OK`

---

#### 8.3.2 Create Category

**Endpoint:** `POST /api/v1/admin/categories`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "name": "Coffee",
  "description": "Coffee products",
  "parent_id": null,
  "is_active": true,
  "sort_order": 0
}
```

**Response:** `201 Created`

---

### 8.4 Payment Method Management

#### 8.4.1 List Payment Methods

**Endpoint:** `GET /api/v1/admin/payment-methods`

**Authentication:** Required (Admin role)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "type": "BANK_TRANSFER",
      "name": "CBE Bank",
      "account_identifier": "1234567890",
      "account_holder": "simpleCommerce Foods",
      "instructions": "Transfer to account number above",
      "is_active": true,
      "sort_order": 0,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

#### 8.4.2 Create Payment Method

**Endpoint:** `POST /api/v1/admin/payment-methods`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "type": "BANK_TRANSFER",
  "name": "CBE Bank",
  "account_identifier": "1234567890",
  "account_holder": "simpleCommerce Foods",
  "instructions": "Transfer to account number above",
  "is_active": true,
  "sort_order": 0
}
```

**Response:** `201 Created`

---

### 8.5 Delivery Zone Management

#### 8.5.1 List Delivery Zones

**Endpoint:** `GET /api/v1/admin/delivery-zones`

**Authentication:** Required (Admin role)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "name": "Addis Ababa Zone A",
      "description": "Central Addis Ababa",
      "fee": "50.00",
      "eta_min_days": 1,
      "eta_max_days": 2,
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

#### 8.5.2 Create Delivery Zone

**Endpoint:** `POST /api/v1/admin/delivery-zones`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "name": "Addis Ababa Zone A",
  "description": "Central Addis Ababa",
  "fee": "50.00",
  "eta_min_days": 1,
  "eta_max_days": 2,
  "is_active": true
}
```

**Response:** `201 Created`

---

### 8.6 User Management

#### 8.6.1 List Users

**Endpoint:** `GET /api/v1/admin/users`

**Authentication:** Required (Admin role)

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `per_page` (integer, optional, default: 20)
- `role` (string, optional): Filter by role
- `search` (string, optional): Search in name, phone, email

**Response:** `200 OK`

---

#### 8.6.2 Create User

**Endpoint:** `POST /api/v1/admin/users`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "phone": "+251912345678",
  "email": "sales@example.com",
  "first_name": "Sales",
  "last_name": "User",
  "role": "sales"
}
```

**Response:** `201 Created`

---

#### 8.6.3 Update User Role

**Endpoint:** `PATCH /api/v1/admin/users/{id}/role`

**Authentication:** Required (Admin role)

**Path Parameters:**
- `id` (uuid, required): User ID

**Request Body:**
```json
{
  "role": "admin"
}
```

**Response:** `200 OK`

---

## 9. Notification Endpoints

### 9.1 List Notifications

**Endpoint:** `GET /api/v1/notifications`

**Description:** Get user's notifications.

**Authentication:** Required

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `per_page` (integer, optional, default: 20)
- `is_read` (boolean, optional): Filter by read status

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": 1,
      "type": "PAYMENT_APPROVED",
      "title": "Payment Approved",
      "message": "Your payment for order ORD-20240115-0001 has been approved",
      "related_order_id": 123,
      "is_read": false,
      "read_at": null,
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

---

### 9.2 Mark Notification as Read

**Endpoint:** `PATCH /api/v1/notifications/{id}/read`

**Authentication:** Required

**Path Parameters:**
- `id` (integer, required): Notification ID

**Response:** `200 OK`

---

### 9.3 Get Unread Count

**Endpoint:** `GET /api/v1/notifications/unread-count`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "data": {
    "count": 3
  }
}
```

---

## 10. Reporting Endpoints

### 10.1 Orders Report

**Endpoint:** `GET /api/v1/admin/reports/orders`

**Authentication:** Required (Admin role)

**Query Parameters:**
- `date_from` (date, required): Start date
- `date_to` (date, required): End date
- `group_by` (string, optional): "day" | "week" | "month" (default: "day")

**Response:** `200 OK`
```json
{
  "data": {
    "summary": {
      "total_orders": 150,
      "orders_by_status": {
        "PENDING_PAYMENT": 10,
        "PAID": 50,
        "DELIVERED": 90
      }
    },
    "daily": [
      {
        "date": "2024-01-15",
        "count": 25
      }
    ]
  }
}
```

---

### 10.2 Revenue Report

**Endpoint:** `GET /api/v1/admin/reports/revenue`

**Authentication:** Required (Admin role)

**Query Parameters:**
- `date_from` (date, required)
- `date_to` (date, required)
- `group_by` (string, optional): "day" | "week" | "month"

**Response:** `200 OK`
```json
{
  "data": {
    "total_revenue": "52500.00",
    "revenue_by_method": {
      "BANK_TRANSFER": "30000.00",
      "MOBILE_MONEY": "22500.00"
    },
    "daily": [
      {
        "date": "2024-01-15",
        "revenue": "3500.00"
      }
    ]
  }
}
```

---

### 10.3 Top Products Report

**Endpoint:** `GET /api/v1/admin/reports/top-products`

**Authentication:** Required (Admin role)

**Query Parameters:**
- `date_from` (date, required)
- `date_to` (date, required)
- `limit` (integer, optional, default: 10): Number of top products

**Response:** `200 OK`
```json
{
  "data": [
    {
      "product_id": 1,
      "product_name": "Ethiopian Coffee Beans",
      "total_quantity_sold": 150,
      "total_revenue": "22500.00"
    }
  ]
}
```

---

## 11. Health Check

### 11.1 Health Check

**Endpoint:** `GET /api/v1/health`

**Description:** Check API health status.

**Authentication:** Not required

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "storage": "connected",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

---

## 12. Error Codes

### 12.1 Standard Error Codes

- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_REQUIRED` - Authentication required
- `AUTHORIZATION_FAILED` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Resource not found
- `RESOURCE_CONFLICT` - Resource conflict (e.g., duplicate)
- `BUSINESS_RULE_VIOLATION` - Business rule violated
- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded
- `INTERNAL_SERVER_ERROR` - Server error

### 12.2 Business Rule Error Codes

- `INSUFFICIENT_STOCK` - Not enough stock available
- `INVALID_STATUS_TRANSITION` - Invalid order status transition
- `ORDER_CANNOT_BE_CANCELLED` - Order cannot be cancelled
- `PAYMENT_ALREADY_SUBMITTED` - Payment already submitted
- `INVALID_OTP` - Invalid or expired OTP
- `PHONE_ALREADY_LINKED` - Phone number already linked to another account

---

## 13. Rate Limiting

### 13.1 Rate Limits

- **OTP Requests:** 3 requests per phone per 15 minutes, 5 requests per IP per 15 minutes
- **API Endpoints:** 100 requests per user per minute (authenticated)
- **File Uploads:** 10 uploads per user per hour

### 13.2 Rate Limit Headers

**Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

---

## 14. Pagination

### 14.1 Pagination Parameters

- `page` (integer): Page number (1-indexed)
- `per_page` (integer): Items per page (default: 20, max: 100)

### 14.2 Pagination Response

```json
{
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## 15. File Upload Specifications

### 15.1 Payment Screenshot

- **Endpoint:** `POST /api/v1/orders/{id}/payment`
- **Content-Type:** `multipart/form-data`
- **File Field:** `screenshot`
- **Allowed Types:** `image/jpeg`, `image/png`
- **Max Size:** 5MB
- **Validation:** Server-side file type and size validation

### 15.2 Product Images

- **Endpoint:** `POST /api/v1/admin/products/{id}/images`
- **Content-Type:** `multipart/form-data`
- **File Field:** `images` (array)
- **Allowed Types:** `image/jpeg`, `image/png`
- **Max Size:** 5MB per image
- **Max Images:** 10 per product

---

## 16. WebSocket/SSE (Future)

### 16.1 Real-time Notifications

**Endpoint:** `GET /api/v1/notifications/stream`

**Description:** Server-Sent Events stream for real-time notifications (future implementation).

**Authentication:** Required

**Response:** `text/event-stream`

---

## 17. API Documentation

### 17.1 OpenAPI/Swagger

- **Swagger UI:** `/docs` (development)
- **ReDoc:** `/redoc` (development)
- **OpenAPI JSON:** `/openapi.json`

### 17.2 API Versioning

- Current version: `v1`
- Future versions: `v2`, `v3`, etc.
- Deprecation policy: 6 months notice before version removal

---

**Document Status:** Draft v1.0  
**Last Updated:** Based on SRS v1.0, Architecture Design v1.0, Database Design v1.0, Functional Requirements v1.0  
**Next Review:** After implementation decisions are made

