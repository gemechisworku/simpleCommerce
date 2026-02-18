import api from './api';
import { Product, PaginatedResponse } from '../types';

export const productService = {
  async list(params?: { page?: number; search?: string; category_id?: number; is_featured?: boolean }) {
    const { data } = await api.get<PaginatedResponse<Product>>('/products', { params });
    return data;
  },

  async getBySlug(slug: string) {
    const { data } = await api.get<{ data: Product }>(`/products/${slug}`);
    return data.data;
  },
};
