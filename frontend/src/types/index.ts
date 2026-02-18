export interface User {
  id: string;
  phone: string | null;
  phone_verified: boolean;
  email: string | null;
  email_verified: boolean;
  first_name: string | null;
  last_name: string | null;
  role: 'customer' | 'sales' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface ApiResponse<T> {
  data: T;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
    has_next?: boolean;
    has_prev?: boolean;
  };
}

export interface ProductVariant {
  id: number;
  label: string;
  price: string;
  stock_qty: number;
  is_active: boolean;
}

export interface ProductImage {
  id: number;
  url: string;
  alt_text?: string | null;
  sort_order: number;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  category_id: number | null;
  is_featured: boolean;
  price_min?: string;
  price_max?: string;
  has_stock?: boolean;
  image_url?: string | null;
  images?: ProductImage[];
  variants?: ProductVariant[];
  created_at: string;
}

export interface CartItem {
  variant_id: number;
  product_id: number;
  product_name: string;
  variant_label: string;
  price: string;
  quantity: number;
  image_url?: string | null;
}

export interface DeliveryZone {
  id: number;
  name: string;
  fee: string;
  eta_min_days: number;
  eta_max_days: number;
  is_active: boolean;
}

export interface OrderItem {
  id: number;
  product_id: number;
  variant_id: number | null;
  product_name: string;
  variant_label: string | null;
  quantity: number;
  unit_price: string;
  line_total: string;
}

export interface OrderStatusHistory {
  id: number;
  new_status: string;
  created_at: string;
  note?: string;
}

export interface Order {
  id: number;
  order_number: string;
  user_id: string;
  status: string;
  subtotal: string;
  delivery_fee: string;
  total: string;
  delivery_address: string;
  recipient_name: string;
  recipient_phone: string;
  delivery_instructions: string | null;
  expected_delivery_from: string | null;
  expected_delivery_to: string | null;
  created_at: string;
  items: OrderItem[];
  status_history?: OrderStatusHistory[];
}

export interface PaymentMethod {
  id: number;
  type: string;
  name: string;
  account_identifier: string;
  account_holder: string;
  instructions: string | null;
}
