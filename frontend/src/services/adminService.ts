import api from './api';
import { Order, Product, DeliveryZone, PaymentMethod } from '../types';

export interface DashboardMetrics {
  orders_today: number;
  pending_payments_count: number;
  orders_by_status: Record<string, number>;
  revenue_today: number;
  recent_orders: Order[];
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  parent_id?: number | null;
  is_active: boolean;
  sort_order?: number;
}

export interface UserListItem {
  id: string;
  phone: string | null;
  email: string | null;
  first_name: string | null;
  last_name: string | null;
  role: string;
  is_active: boolean;
}

export interface PaymentQueueItem {
  id: number;
  order_id: number;
  method_id: number;
  status: string;
  amount_declared: string | null;
  screenshot_url: string;
  created_at: string;
}

export const adminService = {
  async getDashboard() {
    const { data } = await api.get<{ data: DashboardMetrics }>('/admin/dashboard');
    return data.data;
  },

  async listOrders(params?: { page?: number; status?: string }) {
    const res = await api.get<{ data: Order[]; meta: { total_pages: number; total: number } }>('/admin/orders', { params });
    return res.data;
  },

  async getOrder(id: number) {
    const { data } = await api.get<{ data: Order }>(`/admin/orders/${id}`);
    return data.data;
  },

  async updateOrderStatus(orderId: number, status: string, note?: string) {
    const { data } = await api.patch<{ data: Order }>(`/admin/orders/${orderId}/status`, { status, note });
    return data.data;
  },

  async cancelOrder(orderId: number, reason: string) {
    const { data } = await api.post<{ data: Order }>(`/admin/orders/${orderId}/cancel`, { reason });
    return data.data;
  },

  async listPaymentQueue(params?: { page?: number }) {
    const res = await api.get<{ data: PaymentQueueItem[]; meta: { total_pages: number } }>('/payments/queue', { params });
    return res.data;
  },

  async approvePayment(id: number, note?: string) {
    const { data } = await api.post(`/payments/queue/${id}/approve`, { note });
    return data;
  },

  async rejectPayment(id: number, reason: string) {
    const { data } = await api.post(`/payments/queue/${id}/reject`, { reason });
    return data;
  },

  async requestPaymentResubmit(id: number, note?: string) {
    const { data } = await api.post(`/payments/queue/${id}/request-resubmission`, { note });
    return data;
  },

  // Products
  async listProducts(params?: { page?: number; search?: string; category_id?: number; is_active?: boolean }) {
    const res = await api.get<{ data: Product[]; meta: { total_pages: number; total: number } }>('/admin/products', { params });
    return res.data;
  },

  async getProduct(id: number) {
    const { data } = await api.get<{ data: Product }>(`/admin/products/${id}`);
    return data.data;
  },

  async createProduct(payload: { name: string; description?: string; category_id?: number; is_active?: boolean; is_featured?: boolean; variants?: Array<{ label: string; price: string; stock_qty: number; sku?: string }> }) {
    const { data } = await api.post<{ data: Product }>('/admin/products', payload);
    return data.data;
  },

  async updateProduct(id: number, payload: Partial<{ name: string; description: string; category_id: number; is_active: boolean; is_featured: boolean }>) {
    const { data } = await api.patch<{ data: Product }>(`/admin/products/${id}`, payload);
    return data.data;
  },

  async deleteProduct(id: number) {
    await api.delete(`/admin/products/${id}`);
  },

  async createVariant(productId: number, payload: { label: string; price: string; stock_qty: number; sku?: string; is_active?: boolean }) {
    const { data } = await api.post(`/admin/products/${productId}/variants`, payload);
    return data.data;
  },

  async updateVariant(variantId: number, payload: Partial<{ label: string; price: string; stock_qty: number; sku: string; is_active: boolean }>) {
    const { data } = await api.patch(`/admin/products/variants/${variantId}`, payload);
    return data.data;
  },

  async deleteVariant(variantId: number) {
    await api.delete(`/admin/products/variants/${variantId}`);
  },

  async listProductImages(productId: number) {
    const { data } = await api.get<{ data: { id: number; url: string; alt_text?: string | null; sort_order: number }[] }>(`/admin/products/${productId}/images`);
    return data.data;
  },

  async uploadProductImage(productId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post(`/admin/products/${productId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data.data;
  },

  async deleteProductImage(productId: number, imageId: number) {
    await api.delete(`/admin/products/${productId}/images/${imageId}`);
  },

  // Categories
  async listCategories(activeOnly = false) {
    const { data } = await api.get<{ data: Category[] }>('/admin/categories', { params: { active_only: activeOnly } });
    return data.data;
  },

  async createCategory(payload: { name: string; description?: string; parent_id?: number; is_active?: boolean; sort_order?: number }) {
    const { data } = await api.post<{ data: Category }>('/admin/categories', payload);
    return data.data;
  },

  async updateCategory(id: number, payload: Partial<{ name: string; description: string; parent_id: number | null; is_active: boolean; sort_order: number }>) {
    const { data } = await api.patch<{ data: Category }>(`/admin/categories/${id}`, payload);
    return data.data;
  },

  async deleteCategory(id: number) {
    await api.delete(`/admin/categories/${id}`);
  },

  // Delivery Zones
  async listDeliveryZones(activeOnly = false) {
    const { data } = await api.get<{ data: DeliveryZone[] }>('/admin/delivery-zones', { params: { active_only: activeOnly } });
    return data.data;
  },

  async createDeliveryZone(payload: { name: string; description?: string; fee: string; eta_min_days: number; eta_max_days: number; is_active?: boolean }) {
    const { data } = await api.post<{ data: DeliveryZone }>('/admin/delivery-zones', payload);
    return data.data;
  },

  async updateDeliveryZone(id: number, payload: Partial<{ name: string; description: string; fee: string; eta_min_days: number; eta_max_days: number; is_active: boolean }>) {
    const { data } = await api.patch<{ data: DeliveryZone }>(`/admin/delivery-zones/${id}`, payload);
    return data.data;
  },

  // Payment Methods
  async listPaymentMethods(activeOnly = false) {
    const { data } = await api.get<{ data: PaymentMethod[] }>('/admin/payment-methods', { params: { active_only: activeOnly } });
    return data.data;
  },

  async createPaymentMethod(payload: { type: string; name: string; account_identifier: string; account_holder: string; instructions?: string; is_active?: boolean; sort_order?: number }) {
    const { data } = await api.post<{ data: PaymentMethod }>('/admin/payment-methods', payload);
    return data.data;
  },

  async getPaymentMethod(id: number) {
    const { data } = await api.get<{ data: PaymentMethod }>(`/admin/payment-methods/${id}`);
    return data.data;
  },

  async updatePaymentMethod(id: number, payload: Partial<{ name: string; account_identifier: string; account_holder: string; instructions: string; is_active: boolean; sort_order: number }>) {
    const { data } = await api.patch<{ data: PaymentMethod }>(`/admin/payment-methods/${id}`, payload);
    return data.data;
  },

  // Users
  async listUsers(params?: { page?: number; role?: string; search?: string }) {
    const res = await api.get<{ data: UserListItem[]; meta: { total_pages: number; total: number } }>('/admin/users', { params });
    return res.data;
  },

  async createUser(payload: { phone: string; email?: string; first_name?: string; last_name?: string; role: 'sales' | 'admin' }) {
    const { data } = await api.post<{ data: UserListItem }>('/admin/users', payload);
    return data.data;
  },

  async updateUserRole(userId: string, role: string) {
    const { data } = await api.patch(`/admin/users/${userId}/role`, { role });
    return data.data;
  },
};
