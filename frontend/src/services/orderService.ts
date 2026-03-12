import api from './api';
import { Order, PaginatedResponse } from '../types';

export interface OrderCreateInput {
  items: { product_id?: number; variant_id: number; quantity: number }[];
  delivery_zone_id: number;
  delivery_address: string;
  recipient_name: string;
  recipient_phone: string;
  delivery_instructions?: string;
}

export const orderService = {
  async create(orderData: OrderCreateInput) {
    const { data } = await api.post<{ data: Order }>('/orders/checkout', orderData);
    return data.data;
  },

  async listMy(params?: { page?: number; status?: string }) {
    const { data } = await api.get<PaginatedResponse<Order>>('/orders/my', { params });
    return data;
  },

  async getById(id: number) {
    const { data } = await api.get<{ data: Order }>(`/orders/my/${id}`);
    return data.data;
  },

  async cancel(id: number, reason?: string) {
    const { data } = await api.post<{ data: Order }>(`/orders/my/${id}/cancel`, { reason });
    return data.data;
  },
};
