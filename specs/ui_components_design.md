# UI Components Design Document

**Project Name:** simpleCommerce Commerce & Order Operations Platform  
**Version:** 1.0  
**Based on:** Software Requirements Specification v1.0, Architecture Design v1.0, Functional Requirements v1.0

---

## 1. Design Principles

### 1.1 Mobile-First Approach

- All designs prioritize mobile experience
- Responsive breakpoints: Mobile (< 768px), Tablet (768px - 1024px), Desktop (> 1024px)
- Touch-friendly interactive elements (minimum 44x44px)
- Optimized for one-handed mobile usage

### 1.2 User Experience Guidelines

- **Minimal Steps:** Reduce user actions required to complete tasks
- **Clear Feedback:** Visual feedback for all user actions
- **Error Prevention:** Validate inputs before submission
- **Accessibility:** WCAG 2.1 AA compliance
- **Loading States:** Show loading indicators for async operations
- **Error Handling:** Clear, actionable error messages

### 1.3 Component Reusability

- Shared component library for consistency
- Atomic design principles (atoms, molecules, organisms)
- Consistent spacing and typography scale
- Standardized color usage (defined in `_meta.md`)

---

## 2. Layout Components

### 2.1 App Shell

**Structure:**
```
┌─────────────────────────────────────┐
│           Header/Navigation         │
├─────────────────────────────────────┤
│                                     │
│         Main Content Area           │
│                                     │
│                                     │
├─────────────────────────────────────┤
│              Footer                 │
└─────────────────────────────────────┘
```

**Responsive Behavior:**
- Mobile: Collapsible navigation menu (hamburger)
- Desktop: Horizontal navigation bar
- Sticky header on scroll (mobile and desktop)

---

### 2.2 Header/Navigation

**Customer Storefront Header:**

**Mobile:**
```
┌─────────────────────────────────┐
│ [☰]  Logo  [🔍] [🛒] [👤]      │
└─────────────────────────────────┘
```

**Desktop:**
```
┌─────────────────────────────────────────────────────┐
│ Logo  [Products] [Categories] [About]  [🔍] [🛒] [👤]│
└─────────────────────────────────────────────────────┘
```

**Elements:**
- Logo (left-aligned)
- Navigation links (center/left)
- Search icon/input
- Shopping cart icon with item count badge
- User account menu/icon
- Mobile: Hamburger menu icon

**Admin/Sales Dashboard Header:**

**Mobile:**
```
┌─────────────────────────────────┐
│ [☰]  Logo  [🔔] [👤]            │
└─────────────────────────────────┘
```

**Desktop:**
```
┌─────────────────────────────────────────────────────┐
│ Logo  [Dashboard] [Orders] [Payments] [🔔] [👤]    │
└─────────────────────────────────────────────────────┘
```

**Elements:**
- Logo
- Role-based navigation menu
- Notifications icon with unread count badge
- User menu with role indicator

---

### 2.3 Footer

**Customer Storefront Footer:**

```
┌─────────────────────────────────────┐
│  Links Section                      │
│  - About                            │
│  - Contact                          │
│  - Terms                            │
│  - Privacy                          │
├─────────────────────────────────────┤
│  Social Media Icons (optional)      │
├─────────────────────────────────────┤
│  Copyright © 2024                   │
└─────────────────────────────────────┘
```

**Admin Dashboard Footer:**
- Minimal footer with copyright
- Version information (optional)

---

### 2.4 Sidebar (Admin Dashboard - Desktop)

**Desktop Layout:**
```
┌──────┬──────────────────────────────┐
│      │                              │
│ Nav  │     Main Content             │
│ Menu │                              │
│      │                              │
└──────┴──────────────────────────────┘
```

**Navigation Menu Items:**
- Dashboard
- Orders
- Payment Queue
- Products
- Categories
- Inventory
- Payment Methods
- Delivery Zones
- Users (Admin only)
- Reports (Admin only)
- Settings (Admin only)

**Mobile:** Sidebar becomes bottom navigation or drawer menu

---

## 3. Authentication Pages

### 3.1 Login Page

**Layout:**
```
┌─────────────────────────────────┐
│         Logo                     │
│                                  │
│    Welcome Back                  │
│                                  │
│  ┌───────────────────────────┐  │
│  │  Phone Number              │  │
│  │  [________________]        │  │
│  └───────────────────────────┘  │
│                                  │
│  [Request OTP]                   │
│                                  │
│  ───────── OR ─────────          │
│                                  │
│  [Login with Email]              │
│                                  │
│  [Login with Telegram] (optional)│
└─────────────────────────────────┘
```

**Components:**
- Phone input field with country code selector
- "Request OTP" button
- Alternative login methods (email, Telegram)
- Link to terms/privacy (optional)

**OTP Verification Step:**
```
┌─────────────────────────────────┐
│         Logo                     │
│                                  │
│    Enter Verification Code      │
│                                  │
│  Code sent to +251912345678     │
│                                  │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ │
│  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │ │
│  └───┘ └───┘ └───┘ └───┘ └───┘ │
│                                  │
│  [Verify]                        │
│                                  │
│  [Resend OTP] (00:45)           │
│                                  │
│  [Change Phone Number]           │
└─────────────────────────────────┘
```

**Components:**
- 6-digit OTP input (auto-focus, auto-submit on complete)
- Verify button
- Resend OTP button with countdown timer
- Change phone number link

**States:**
- Loading state during OTP request
- Error message display
- Success state (redirects to appropriate dashboard)

---

### 3.2 Email Login Page

**Similar structure to phone login:**
- Email input field
- Request OTP/Magic Link button
- Verification step (OTP input or magic link confirmation)

---

## 4. Customer Storefront Pages

### 4.1 Home/Product Listing Page

**Layout:**
```
┌─────────────────────────────────┐
│  [Search Bar]                   │
├─────────────────────────────────┤
│  [Categories Filter]             │
│  [All] [Coffee] [Tea] [Spices]  │
├─────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐  │
│  │Image │  │Image │  │Image │  │
│  │      │  │      │  │      │  │
│  │Name  │  │Name  │  │Name  │  │
│  │Price │  │Price │  │Price │  │
│  │[Add] │  │[Add] │  │[Add] │  │
│  └──────┘  └──────┘  └──────┘  │
│                                  │
│  ┌──────┐  ┌──────┐  ┌──────┐  │
│  │ ...  │  │ ...  │  │ ...  │  │
│  └──────┘  └──────┘  └──────┘  │
├─────────────────────────────────┤
│  [Load More] or [1] [2] [3] ... │
└─────────────────────────────────┘
```

**Components:**
- Search bar (sticky on scroll)
- Category filter chips
- Product grid (2 columns mobile, 3-4 columns desktop)
- Product card component
- Pagination or infinite scroll
- Loading skeleton placeholders

**Product Card:**
```
┌─────────────────┐
│                 │
│   Product Image │
│                 │
├─────────────────┤
│ Product Name    │
│ Price Range     │
│ [Add to Cart]   │
│ Stock: In Stock │
└─────────────────┘
```

**States:**
- In stock: Green indicator, enabled "Add to Cart"
- Out of stock: Red indicator, disabled "Add to Cart"
- Loading: Skeleton placeholder

---

### 4.2 Product Detail Page

**Layout:**
```
┌─────────────────────────────────┐
│  [← Back]                        │
├─────────────────────────────────┤
│  ┌──────────┐                    │
│  │          │                    │
│  │  Image   │  Product Name      │
│  │  Gallery │  Price: 150.00 ETB │
│  │          │                    │
│  │  [◄] [►] │  Variant: [250g ▼] │
│  └──────────┘                    │
│                                  │
│  Description:                    │
│  Lorem ipsum...                  │
│                                  │
│  Stock: 50 available             │
│                                  │
│  Quantity: [−] 1 [+]              │
│                                  │
│  [Add to Cart]                   │
│                                  │
│  ─────────────────────────────   │
│                                  │
│  Related Products                │
│  [Product cards grid]             │
└─────────────────────────────────┘
```

**Components:**
- Image gallery with thumbnails
- Product name and description
- Variant selector (dropdown or buttons)
- Price display (updates based on variant)
- Stock availability indicator
- Quantity selector
- Add to Cart button
- Related products section

**Image Gallery:**
- Main image (large)
- Thumbnail strip below (scrollable on mobile)
- Swipeable on mobile
- Lightbox on click (desktop)

---

### 4.3 Shopping Cart Page

**Layout:**
```
┌─────────────────────────────────┐
│  Shopping Cart                  │
├─────────────────────────────────┤
│  ┌───────────────────────────┐  │
│  │ [Image] Product Name       │  │
│  │         Variant: 250g      │  │
│  │         Price: 150.00      │  │
│  │  Qty: [−] 2 [+] [Remove]   │  │
│  └───────────────────────────┘  │
│                                  │
│  ┌───────────────────────────┐  │
│  │ [Image] Product Name       │  │
│  │         Variant: 1kg       │  │
│  │         Price: 550.00      │  │
│  │  Qty: [−] 1 [+] [Remove]   │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  Subtotal:        1,250.00      │
│  Delivery Fee:       50.00      │
│  ────────────────────────────   │
│  Total:           1,300.00      │
│                                  │
│  [Proceed to Checkout]           │
│                                  │
│  [Continue Shopping]             │
└─────────────────────────────────┘
```

**Components:**
- Cart item list
- Cart item component (image, name, variant, price, quantity controls)
- Remove item button
- Price summary (subtotal, delivery fee, total)
- Proceed to Checkout button
- Empty cart state

**Empty Cart State:**
- Empty cart icon
- "Your cart is empty" message
- "Browse Products" button

---

### 4.4 Checkout Page

**Layout:**
```
┌─────────────────────────────────┐
│  Checkout                        │
├─────────────────────────────────┤
│  Delivery Information            │
│  ┌───────────────────────────┐  │
│  │ Full Address              │  │
│  │ [___________________]     │  │
│  │                          │  │
│  │ Recipient Name            │  │
│  │ [___________________]     │  │
│  │                          │  │
│  │ Phone                     │  │
│  │ [___________________]     │  │
│  │                          │  │
│  │ Delivery Zone             │  │
│  │ [Select Zone ▼]           │  │
│  │                          │  │
│  │ Instructions (optional)   │  │
│  │ [___________________]     │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  Order Summary                   │
│  ┌───────────────────────────┐  │
│  │ Items (2)                  │  │
│  │ • Product 1 x2   300.00   │  │
│  │ • Product 2 x1   550.00   │  │
│  │                          │  │
│  │ Subtotal:        850.00   │  │
│  │ Delivery:         50.00   │  │
│  │ ──────────────────────── │  │
│  │ Total:           900.00   │  │
│  │                          │  │
│  │ ETA: Jan 16 - Jan 17     │  │
│  └───────────────────────────┘  │
│                                  │
│  [Place Order]                   │
└─────────────────────────────────┘
```

**Components:**
- Delivery address form
- Recipient information form
- Delivery zone selector (updates fee and ETA)
- Order summary card (sticky on desktop)
- Real-time fee calculation
- Form validation
- Place Order button

**Validation:**
- Real-time field validation
- Error messages below fields
- Disable submit until valid

---

### 4.5 Payment Instructions Page

**Layout:**
```
┌─────────────────────────────────┐
│  ✓ Order Placed Successfully    │
│                                  │
│  Order #: ORD-20240115-0001     │
│  Total Amount: 900.00 ETB        │
│  Expected Delivery: Jan 16-17   │
├─────────────────────────────────┤
│  Payment Instructions            │
│                                  │
│  Please transfer the amount to:  │
│                                  │
│  ┌───────────────────────────┐  │
│  │ CBE Bank                  │  │
│  │ Account: 1234567890       │  │
│  │ [Copy]                    │  │
│  │                           │  │
│  │ Account Holder:           │  │
│  │ Melegna Foods             │  │
│  │ [Copy]                    │  │
│  │                           │  │
│  │ Instructions:             │  │
│  │ Transfer to account...    │  │
│  └───────────────────────────┘  │
│                                  │
│  ───────── OR ─────────          │
│                                  │
│  [Other Payment Methods ▼]       │
│                                  │
├─────────────────────────────────┤
│  After Payment:                  │
│                                  │
│  [Upload Payment Screenshot]     │
│                                  │
│  [Track Order]                   │
└─────────────────────────────────┘
```

**Components:**
- Order confirmation message
- Order number and details
- Payment method cards (expandable)
- Copy-to-clipboard buttons for account details
- Upload payment screenshot button
- Track order link

**Payment Method Card:**
- Method name and type
- Account number/wallet ID (copyable)
- Account holder name (copyable)
- Instructions text

---

### 4.6 Payment Upload Page

**Layout:**
```
┌─────────────────────────────────┐
│  Upload Payment Proof            │
│                                  │
│  Order #: ORD-20240115-0001     │
│  Amount: 900.00 ETB              │
├─────────────────────────────────┤
│  Payment Method                  │
│  [Select Method ▼]               │
│                                  │
│  Upload Screenshot               │
│  ┌───────────────────────────┐  │
│  │                           │  │
│  │    [📷 Upload Image]      │  │
│  │                           │  │
│  │  or drag and drop         │  │
│  │                           │  │
│  │  JPG, PNG up to 5MB       │  │
│  └───────────────────────────┘  │
│                                  │
│  Optional Information            │
│  ┌───────────────────────────┐  │
│  │ Amount Paid                │  │
│  │ [___________________]      │  │
│  │                           │  │
│  │ Transaction Reference      │  │
│  │ [___________________]      │  │
│  │                           │  │
│  │ Payment Date               │  │
│  │ [Date Picker]              │  │
│  └───────────────────────────┘  │
│                                  │
│  [Submit Payment]                │
│                                  │
│  [Cancel]                        │
└─────────────────────────────────┘
```

**Components:**
- Payment method selector
- File upload area (drag & drop)
- Image preview after upload
- Optional payment details form
- Submit button
- File validation feedback

**File Upload States:**
- Empty: Upload prompt
- Uploading: Progress indicator
- Uploaded: Image preview with remove option
- Error: Error message

---

### 4.7 My Orders Page

**Layout:**
```
┌─────────────────────────────────┐
│  My Orders                      │
├─────────────────────────────────┤
│  [All] [Pending] [Paid] [Delivered]│
├─────────────────────────────────┤
│  ┌───────────────────────────┐  │
│  │ Order #ORD-20240115-0001  │  │
│  │ Date: Jan 15, 2024        │  │
│  │ Status: [PAID]             │  │
│  │                           │  │
│  │ Items: 2                  │  │
│  │ Total: 900.00 ETB         │  │
│  │                           │  │
│  │ [View Details]             │  │
│  └───────────────────────────┘  │
│                                  │
│  ┌───────────────────────────┐  │
│  │ Order #ORD-20240114-0005  │  │
│  │ Date: Jan 14, 2024        │  │
│  │ Status: [DELIVERED]        │  │
│  │                           │  │
│  │ Items: 1                  │  │
│  │ Total: 350.00 ETB         │  │
│  │                           │  │
│  │ [View Details]             │  │
│  └───────────────────────────┘  │
│                                  │
│  [Load More]                     │
└─────────────────────────────────┘
```

**Components:**
- Status filter tabs
- Order list cards
- Order card component
- Pagination or infinite scroll
- Empty state

**Order Card:**
- Order number
- Order date
- Status badge (color-coded)
- Item count
- Total amount
- View Details button

---

### 4.8 Order Detail/Tracking Page

**Layout:**
```
┌─────────────────────────────────┐
│  [← Back to Orders]              │
├─────────────────────────────────┤
│  Order #ORD-20240115-0001       │
│  Placed on Jan 15, 2024         │
│  Status: [PAID]                 │
├─────────────────────────────────┤
│  Order Timeline                  │
│  ┌───────────────────────────┐  │
│  │ ● PENDING_PAYMENT         │  │
│  │   Jan 15, 10:00 AM        │  │
│  │                           │  │
│  │ ● PAYMENT_SUBMITTED       │  │
│  │   Jan 15, 10:30 AM        │  │
│  │                           │  │
│  │ ● PAID                    │  │
│  │   Jan 15, 11:00 AM        │  │
│  │   Verified by Sales        │  │
│  │                           │  │
│  │ ○ PACKING                 │  │
│  │                           │  │
│  │ ○ DISPATCHED               │  │
│  │                           │  │
│  │ ○ DELIVERED                │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  Order Items                     │
│  ┌───────────────────────────┐  │
│  │ [Image] Product Name      │  │
│  │ Variant: 250g             │  │
│  │ Qty: 2 × 150.00 = 300.00 │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  Delivery Information            │
│  Address: 123 Main St...         │
│  Recipient: John Doe             │
│  Phone: +251912345678            │
│  ETA: Jan 16 - Jan 17           │
├─────────────────────────────────┤
│  Payment Information             │
│  Method: CBE Bank                │
│  Status: Approved                │
│  [View Screenshot]               │
├─────────────────────────────────┤
│  Order Summary                   │
│  Subtotal:        850.00         │
│  Delivery:         50.00         │
│  ────────────────────────────   │
│  Total:           900.00         │
│                                  │
│  [Cancel Order] (if allowed)     │
└─────────────────────────────────┘
```

**Components:**
- Order header with status
- Status timeline (visual progress indicator)
- Order items list
- Delivery information
- Payment information
- Order summary
- Cancel order button (conditional)

**Status Timeline:**
- Completed steps: Filled circle, green
- Current step: Filled circle, blue, animated
- Future steps: Empty circle, gray
- Timestamps and actor names

---

### 4.9 User Account Page

**Layout:**
```
┌─────────────────────────────────┐
│  My Account                      │
├─────────────────────────────────┤
│  Profile Information             │
│  ┌───────────────────────────┐  │
│  │ Phone: +251912345678      │  │
│  │ [Edit]                    │  │
│  │                           │  │
│  │ Email: user@example.com   │  │
│  │ [Edit] [Verify]           │  │
│  │                           │  │
│  │ Name: John Doe            │  │
│  │ [Edit]                    │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  Saved Addresses                 │
│  [Add New Address]               │
│  ┌───────────────────────────┐  │
│  │ 123 Main Street           │  │
│  │ Addis Ababa               │  │
│  │ [Edit] [Delete] [Set Default]│
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  [My Orders]                     │
│  [Notifications]                 │
│  [Logout]                        │
└─────────────────────────────────┘
```

**Components:**
- Profile information display
- Editable fields
- Saved addresses list
- Navigation links
- Logout button

---

## 5. Admin/Sales Dashboard Pages

### 5.1 Dashboard Overview

**Layout:**
```
┌─────────────────────────────────┐
│  Dashboard                       │
├─────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐     │
│  │ Orders   │ │ Payments │     │
│  │ Today    │ │ Pending  │     │
│  │   25     │ │    12    │     │
│  └──────────┘ └──────────┘     │
│                                  │
│  ┌──────────┐ ┌──────────┐     │
│  │ Revenue  │ │ Status   │     │
│  │ Today    │ │ Breakdown│     │
│  │ 3,500.00 │ │ [Chart]  │     │
│  └──────────┘ └──────────┘     │
├─────────────────────────────────┤
│  Recent Orders                   │
│  [Order list table/cards]        │
└─────────────────────────────────┘
```

**Components:**
- Stat cards (orders, payments, revenue)
- Charts/graphs (status breakdown, revenue trend)
- Recent orders table
- Quick action buttons

**Stat Card:**
- Icon
- Label
- Value (large, prominent)
- Change indicator (optional)

---

### 5.2 Orders Management Page

**Layout:**
```
┌─────────────────────────────────┐
│  Orders                         │
├─────────────────────────────────┤
│  [Filters] [Search] [Export]    │
├─────────────────────────────────┤
│  Status: [All ▼] Date: [Range]  │
│  Customer: [Search]             │
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ Order# │ Date │ Customer   │ │
│  │ Status │ Total│ [Actions]  │ │
│  ├────────────────────────────┤ │
│  │ ORD-001│ Jan15│ John Doe   │ │
│  │ PAID   │ 900  │ [View] [⚙] │ │
│  ├────────────────────────────┤ │
│  │ ORD-002│ Jan15│ Jane Smith │ │
│  │ PENDING│ 350  │ [View] [⚙] │ │
│  └────────────────────────────┘ │
│                                  │
│  [1] [2] [3] ... [Next]          │
└─────────────────────────────────┘
```

**Components:**
- Filter bar
- Search input
- Orders table (desktop) or cards (mobile)
- Status badges
- Action buttons (View, Update Status)
- Pagination

**Table View (Desktop):**
- Sortable columns
- Row selection (optional)
- Bulk actions (optional)

**Card View (Mobile):**
- Order card with key information
- Expandable details
- Quick actions

---

### 5.3 Order Detail Page (Admin/Sales)

**Layout:**
```
┌─────────────────────────────────┐
│  [← Back] Order #ORD-20240115-0001│
├─────────────────────────────────┤
│  Status: [PAID ▼] [Update Status]│
├─────────────────────────────────┤
│  Customer Information            │
│  Name: John Doe                  │
│  Phone: +251912345678            │
│  Email: user@example.com         │
├─────────────────────────────────┤
│  Order Items                     │
│  [Table with items]              │
├─────────────────────────────────┤
│  Delivery Information            │
│  Address: 123 Main St...         │
│  Zone: Addis Ababa Zone A        │
│  ETA: Jan 16 - Jan 17           │
├─────────────────────────────────┤
│  Payment Information             │
│  [Payment details]               │
├─────────────────────────────────┤
│  Status History                  │
│  [Timeline component]            │
├─────────────────────────────────┤
│  [Cancel Order] [Print]          │
└─────────────────────────────────┘
```

**Components:**
- Status selector/updater
- Customer information section
- Order items table
- Delivery information
- Payment information
- Status history timeline
- Action buttons

---

### 5.4 Payment Review Queue Page

**Layout:**
```
┌─────────────────────────────────┐
│  Payment Review Queue            │
│  [12 pending]                    │
├─────────────────────────────────┤
│  [Filters] [Sort: Oldest First] │
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ Order: ORD-001              │ │
│  │ Customer: John Doe         │ │
│  │ Amount: 900.00 ETB         │ │
│  │ Method: CBE Bank           │ │
│  │                           │ │
│  │ [View Screenshot]          │ │
│  │                           │ │
│  │ [Approve] [Reject] [Request│ │
│  │          Resubmission]     │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ [Next Payment Card]         │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

**Components:**
- Pending count badge
- Filter and sort controls
- Payment review cards
- Screenshot viewer (modal/lightbox)
- Quick action buttons (Approve, Reject, Request Resubmission)
- Review note input (optional)

**Payment Review Card:**
- Order information
- Customer information
- Payment method
- Amount declared
- Screenshot thumbnail (clickable)
- Action buttons
- Note input field

**Screenshot Viewer Modal:**
- Full-size image
- Zoom controls
- Close button
- Order context information

---

### 5.5 Product Management Page

**Layout:**
```
┌─────────────────────────────────┐
│  Products  [+ New Product]      │
├─────────────────────────────────┤
│  [Search] [Category Filter]     │
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ [Image] Product Name         │ │
│  │        Category           │ │
│  │        Price: 150.00      │ │
│  │        Stock: 50          │ │
│  │        Status: Active     │ │
│  │                           │ │
│  │ [Edit] [Delete] [View]    │ │
│  └────────────────────────────┘ │
│                                  │
│  [Product cards grid]            │
└─────────────────────────────────┘
```

**Components:**
- Add new product button
- Search and filter controls
- Product cards/list
- Product actions (Edit, Delete, View)
- Status indicators

---

### 5.6 Product Create/Edit Form

**Layout:**
```
┌─────────────────────────────────┐
│  [← Back] Create Product        │
├─────────────────────────────────┤
│  Basic Information               │
│  ┌───────────────────────────┐  │
│  │ Name *                    │  │
│  │ [___________________]     │  │
│  │                           │  │
│  │ Description               │  │
│  │ [___________________]      │  │
│  │ [Text Editor]             │  │
│  │                           │  │
│  │ Category                  │  │
│  │ [Select Category ▼]       │  │
│  │                           │  │
│  │ ☑ Featured                │  │
│  │ ☑ Active                  │  │
│  └───────────────────────────┘  │
├─────────────────────────────────┤
│  Images                          │
│  [Upload Images]                 │
│  [Image gallery with remove]     │
├─────────────────────────────────┤
│  Variants                        │
│  [+ Add Variant]                 │
│  ┌───────────────────────────┐  │
│  │ Label: [250g]             │  │
│  │ Price: [150.00]           │  │
│  │ Stock: [50]               │  │
│  │ SKU: [COFFEE-250G]        │  │
│  │ [Remove]                  │  │
│  └───────────────────────────┘  │
│                                  │
│  [Save Product] [Cancel]         │
└─────────────────────────────────┘
```

**Components:**
- Form fields (name, description, category)
- Checkboxes (featured, active)
- Image upload component
- Variant management (add/remove variants)
- Save and cancel buttons

---

### 5.7 Category Management Page

**Layout:**
```
┌─────────────────────────────────┐
│  Categories  [+ New Category]   │
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ Coffee                      │ │
│  │ 15 products                │ │
│  │ [Edit] [Delete]            │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ Tea                         │ │
│  │ 8 products                 │ │
│  │ [Edit] [Delete]            │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

**Components:**
- Category list/cards
- Product count per category
- Add new category button
- Edit and delete actions

---

### 5.8 Inventory Management Page

**Layout:**
```
┌─────────────────────────────────┐
│  Inventory                       │
├─────────────────────────────────┤
│  [Search Product] [Low Stock Filter]│
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ Product: Coffee Beans       │ │
│  │ Variant: 250g              │ │
│  │ Current Stock: 50          │ │
│  │ [Update Stock]              │ │
│  └────────────────────────────┘ │
│                                  │
│  [Product/Variant list]          │
└─────────────────────────────────┘
```

**Components:**
- Product/variant list
- Stock quantity display
- Quick stock update input
- Low stock warnings
- Bulk update (optional)

---

### 5.9 Payment Methods Management Page

**Layout:**
```
┌─────────────────────────────────┐
│  Payment Methods [+ New Method]  │
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ CBE Bank                   │ │
│  │ Type: Bank Transfer        │ │
│  │ Account: 1234567890        │ │
│  │ Status: Active             │ │
│  │ [Edit] [Delete]            │ │
│  └────────────────────────────┘ │
│                                  │
│  [Payment method cards]          │
└─────────────────────────────────┘
```

**Components:**
- Payment method list
- Method details display
- Add new method button
- Edit and delete actions
- Active/inactive toggle

---

### 5.10 Delivery Zones Management Page

**Layout:**
```
┌─────────────────────────────────┐
│  Delivery Zones [+ New Zone]    │
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ Addis Ababa Zone A         │ │
│  │ Fee: 50.00 ETB             │ │
│  │ ETA: 1-2 days              │ │
│  │ Status: Active             │ │
│  │ [Edit] [Delete]            │ │
│  └────────────────────────────┘ │
│                                  │
│  [Zone cards/list]               │
└─────────────────────────────────┘
```

**Components:**
- Zone list
- Zone details (name, fee, ETA)
- Add new zone button
- Edit and delete actions

---

### 5.11 User Management Page (Admin Only)

**Layout:**
```
┌─────────────────────────────────┐
│  Users  [+ New User]            │
├─────────────────────────────────┤
│  [Search] [Role Filter]         │
├─────────────────────────────────┤
│  ┌────────────────────────────┐ │
│  │ John Doe                   │ │
│  │ +251912345678             │ │
│  │ Role: Customer            │ │
│  │ [Edit] [Change Role]       │ │
│  └────────────────────────────┘ │
│                                  │
│  [User list]                     │
└─────────────────────────────────┘
```

**Components:**
- User list/table
- User information display
- Role badge
- Add new user button
- Edit and role change actions

---

### 5.12 Reports Page (Admin Only)

**Layout:**
```
┌─────────────────────────────────┐
│  Reports                         │
├─────────────────────────────────┤
│  [Orders] [Revenue] [Products]   │
├─────────────────────────────────┤
│  Date Range: [From] [To]        │
│  [Generate Report] [Export CSV] │
├─────────────────────────────────┤
│  Orders Report                   │
│  ┌────────────────────────────┐ │
│  │ Total Orders: 150          │ │
│  │                           │ │
│  │ [Chart/Graph]              │ │
│  │                           │ │
│  │ Status Breakdown:         │ │
│  │ • Pending: 10             │ │
│  │ • Paid: 50                │ │
│  │ • Delivered: 90            │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

**Components:**
- Report type tabs
- Date range selector
- Generate button
- Export button
- Charts and graphs
- Summary statistics
- Data tables

---

## 6. Shared Components

### 6.1 Buttons

**Primary Button:**
- Solid background color
- White text
- Rounded corners
- Hover and active states
- Loading state (spinner)

**Secondary Button:**
- Outlined style
- Transparent background
- Border color

**Text Button:**
- Text only
- No background
- Underline on hover

**Icon Button:**
- Circular or square
- Icon only
- Tooltip on hover

**Button Sizes:**
- Small: Compact, for dense UIs
- Medium: Default size
- Large: Prominent actions

---

### 6.2 Form Components

**Input Field:**
```
┌─────────────────────────┐
│ Label                   │
│ ┌─────────────────────┐ │
│ │ [Input text]        │ │
│ └─────────────────────┘ │
│ Helper text / Error     │
└─────────────────────────┘
```

**Textarea:**
- Resizable (optional)
- Character count (optional)
- Same structure as input

**Select/Dropdown:**
- Custom styled select
- Searchable (for long lists)
- Multi-select support (where needed)

**Checkbox:**
- Custom styled checkbox
- Label on right
- Indeterminate state support

**Radio Button:**
- Custom styled radio
- Grouped with labels

**File Upload:**
- Drag and drop area
- File browser button
- File list with remove
- Progress indicator

---

### 6.3 Cards

**Product Card:**
- Image (top)
- Title
- Price
- Action button
- Stock indicator

**Order Card:**
- Order number
- Date
- Status badge
- Item count
- Total amount
- Action buttons

**Info Card:**
- Icon (optional)
- Title
- Content
- Action (optional)

---

### 6.4 Modals/Dialogs

**Structure:**
```
┌─────────────────────────────┐
│  [X]                        │
│                             │
│  Modal Title                │
│                             │
│  Modal Content              │
│                             │
│  [Cancel] [Confirm]         │
└─────────────────────────────┘
```

**Types:**
- Confirmation modal
- Form modal
- Image viewer modal
- Info modal

**Features:**
- Backdrop overlay
- Close on backdrop click (optional)
- Close on Escape key
- Focus trap
- Scrollable content

---

### 6.5 Notifications

**Toast Notification:**
```
┌─────────────────────────────┐
│ [Icon] Success message      │
│         [X]                 │
└─────────────────────────────┘
```

**Types:**
- Success (green)
- Error (red)
- Warning (yellow)
- Info (blue)

**Position:** Top-right (desktop), Top-center (mobile)

**Behavior:**
- Auto-dismiss after 5 seconds
- Manual dismiss button
- Stack multiple notifications

**In-App Notification Badge:**
- Bell icon with count badge
- Dropdown list of notifications
- Mark as read functionality
- Link to notification detail

---

### 6.6 Loading States

**Spinner:**
- Circular spinner
- Centered in container
- Size variants

**Skeleton Loader:**
- Placeholder shapes matching content
- Shimmer animation
- Used for lists, cards, pages

**Progress Bar:**
- Linear progress indicator
- Percentage display (optional)
- Used for file uploads, long operations

---

### 6.7 Empty States

**Structure:**
```
┌─────────────────────────────┐
│                             │
│        [Icon/Illustration]   │
│                             │
│      Empty State Title      │
│                             │
│    Empty State Message      │
│                             │
│      [Action Button]        │
│                             │
└─────────────────────────────┘
```

**Examples:**
- Empty cart
- No orders
- No products
- No search results

---

### 6.8 Error States

**Error Page (404, 500, etc.):**
```
┌─────────────────────────────┐
│        [Error Icon]         │
│                             │
│      Error Title            │
│                             │
│    Error Message            │
│                             │
│  [Go Home] [Retry]          │
└─────────────────────────────┘
```

**Inline Error:**
- Red text below input field
- Error icon (optional)
- Clear, actionable message

---

### 6.9 Status Badges

**Order Status Badges:**
- PENDING_PAYMENT: Yellow
- PAYMENT_SUBMITTED: Blue
- PAID: Green
- PACKING: Purple
- DISPATCHED: Orange
- DELIVERED: Dark green
- CANCELLED: Red
- PAYMENT_REJECTED: Red

**Payment Status Badges:**
- submitted: Blue
- approved: Green
- rejected: Red
- resubmit_requested: Yellow

**Product Status:**
- Active: Green
- Inactive: Gray
- Out of Stock: Red

---

### 6.10 Tables

**Desktop Table:**
- Sortable columns
- Row hover highlight
- Alternating row colors (optional)
- Responsive scroll (mobile)

**Mobile Table:**
- Card-based layout
- Key information visible
- Expandable details

**Features:**
- Pagination
- Row selection (optional)
- Bulk actions (optional)

---

### 6.11 Search Component

**Search Bar:**
```
┌─────────────────────────────┐
│ [🔍] [Search input] [X]     │
└─────────────────────────────┘
```

**Features:**
- Auto-focus on mobile
- Clear button
- Search suggestions (optional)
- Recent searches (optional)

---

### 6.12 Pagination

**Desktop:**
```
[Previous] [1] [2] [3] ... [10] [Next]
```

**Mobile:**
```
[Previous] Page 1 of 10 [Next]
[Load More] (alternative)
```

**Features:**
- Page numbers
- Previous/Next buttons
- Jump to page (optional)
- Items per page selector

---

### 6.13 Image Gallery

**Product Image Gallery:**
- Main image (large)
- Thumbnail strip
- Zoom on click (desktop)
- Swipeable (mobile)
- Lightbox viewer

**Features:**
- Image navigation (prev/next)
- Fullscreen mode
- Image counter (1/5)

---

### 6.14 Quantity Selector

```
[−] [1] [+]
```

**Features:**
- Decrement button
- Input field (editable)
- Increment button
- Min/max validation
- Disable buttons at limits

---

### 6.15 Copy-to-Clipboard Component

**Structure:**
```
Account Number: 1234567890 [Copy]
```

**Features:**
- Copy button/icon
- Visual feedback on copy
- Tooltip confirmation
- Copy icon changes to checkmark

---

## 7. Responsive Breakpoints

### 7.1 Mobile (< 768px)

- Single column layouts
- Stacked form fields
- Bottom navigation or hamburger menu
- Full-width buttons
- Card-based lists instead of tables
- Swipeable components
- Touch-optimized interactions

### 7.2 Tablet (768px - 1024px)

- Two-column layouts where appropriate
- Sidebar navigation (collapsible)
- Mixed card and table views
- Optimized spacing

### 7.3 Desktop (> 1024px)

- Multi-column layouts
- Sidebar navigation (persistent)
- Table views
- Hover states
- Keyboard navigation
- Wider content areas

---

## 8. Interaction Patterns

### 8.1 Navigation

- **Breadcrumbs:** For deep navigation (Admin)
- **Back Button:** Mobile navigation
- **Tab Navigation:** For related content sections
- **Sidebar:** Admin dashboard navigation

### 8.2 Form Interactions

- **Real-time Validation:** Show errors as user types
- **Auto-save:** For long forms (optional)
- **Progressive Disclosure:** Show advanced options on demand
- **Smart Defaults:** Pre-fill known information

### 8.3 Feedback

- **Loading States:** Show during async operations
- **Success Messages:** Confirm successful actions
- **Error Messages:** Clear, actionable errors
- **Confirmation Dialogs:** For destructive actions

### 8.4 Gestures (Mobile)

- **Swipe:** Navigate between images, dismiss items
- **Pull to Refresh:** Refresh lists
- **Long Press:** Context menus
- **Pinch to Zoom:** Image viewing

---

## 9. Accessibility Requirements

### 9.1 Keyboard Navigation

- All interactive elements keyboard accessible
- Tab order logical
- Focus indicators visible
- Skip links for main content

### 9.2 Screen Readers

- Semantic HTML
- ARIA labels where needed
- Alt text for images
- Form labels associated with inputs

### 9.3 Visual Accessibility

- Sufficient color contrast (WCAG AA)
- Text resizable up to 200%
- Focus indicators
- Error states not color-only

### 9.4 Touch Targets

- Minimum 44x44px touch targets
- Adequate spacing between interactive elements
- No hover-only interactions on mobile

---

## 10. Animation and Transitions

### 10.1 Page Transitions

- Smooth page transitions
- Loading state animations
- Fade in/out for modals

### 10.2 Micro-interactions

- Button hover effects
- Form field focus states
- Success checkmark animation
- Loading spinner

### 10.3 Performance

- Optimize animations (60fps)
- Reduce motion for accessibility
- Lazy load images
- Progressive image loading

---

## 11. Data Display Patterns

### 11.1 Lists

- **Vertical List:** Standard list layout
- **Grid:** Product grid, card grid
- **Table:** Admin data tables
- **Timeline:** Order status history

### 11.2 Data Visualization

- **Charts:** Line, bar, pie charts for reports
- **Progress Indicators:** Order status, upload progress
- **Counters:** Cart count, notification count

### 11.3 Information Hierarchy

- **Headings:** Clear hierarchy (H1-H6)
- **Typography Scale:** Consistent sizing
- **Spacing:** Adequate whitespace
- **Grouping:** Related information grouped

---

## 12. State Management Indicators

### 12.1 Loading States

- Skeleton loaders for content
- Spinners for actions
- Progress bars for uploads
- Disabled states during operations

### 12.2 Error States

- Inline form errors
- Error pages (404, 500)
- Error toasts
- Retry mechanisms

### 12.3 Success States

- Success toasts
- Confirmation messages
- Visual checkmarks
- Redirect after success

### 12.4 Empty States

- Empty cart illustration
- No results message
- Call-to-action buttons
- Helpful guidance

---

## 13. Component States

### 13.1 Button States

- Default
- Hover
- Active/Pressed
- Disabled
- Loading

### 13.2 Input States

- Default
- Focus
- Filled
- Error
- Disabled

### 13.3 Card States

- Default
- Hover (desktop)
- Selected
- Loading
- Error

---

## 14. Mobile-Specific Considerations

### 14.1 Navigation

- Bottom navigation bar (optional)
- Hamburger menu
- Swipe gestures
- Back button handling

### 14.2 Forms

- Appropriate input types (tel, email, etc.)
- Numeric keypad for numbers
- Date pickers optimized for mobile
- Large touch targets

### 14.3 Performance

- Optimized images
- Lazy loading
- Infinite scroll for lists
- Reduced animations on low-end devices

---

## 15. Admin-Specific UI Patterns

### 15.1 Data Tables

- Sortable columns
- Filterable rows
- Bulk actions
- Export functionality

### 15.2 Quick Actions

- One-click approve/reject
- Bulk status updates
- Quick filters
- Keyboard shortcuts (optional)

### 15.3 Dashboard Widgets

- Stat cards
- Charts and graphs
- Recent activity feeds
- Quick links

---

## 16. Component Library Structure

### 16.1 Atomic Components

- Buttons
- Inputs
- Labels
- Icons
- Badges
- Spinners

### 16.2 Molecular Components

- Form fields (label + input + error)
- Search bar
- Product card
- Order card
- Status badge

### 16.3 Organism Components

- Navigation header
- Product grid
- Order list
- Payment review card
- Form sections

### 16.4 Template Components

- Page layouts
- Dashboard layout
- Form layouts
- List layouts

### 16.5 Page Components

- Home page
- Product detail page
- Checkout page
- Admin dashboard
- Order management page

---

**Document Status:** Draft v1.0  
**Last Updated:** Based on SRS v1.0, Architecture Design v1.0, Functional Requirements v1.0  
**Next Review:** After UI/UX design decisions are made

