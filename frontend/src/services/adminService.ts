import api from './api';
import { Order } from '../types';

export interface DashboardMetrics {
  orders_today: number;
  pending_payments_count: number;
  orders_by_status: Record<string, number>;
  revenue_today: number;
  recent_orders: Order[];
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

  async listPaymentQueue(params?: { page?: number }) {
    const { data } = await api.get('/payments/queue', { params });
    return data;
  },
};
