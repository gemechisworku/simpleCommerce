import api from './api';
import { PaymentMethod } from '../types';

export const paymentService = {
  async listMethods() {
    const { data } = await api.get<{ data: PaymentMethod[] }>('/orders/payment-methods');
    return data.data;
  },

  async submit(orderId: number, methodId: number, file: File, amount?: number, reference?: string) {
    const formData = new FormData();
    formData.append('file', file);
    const params = new URLSearchParams({
      order_id: String(orderId),
      method_id: String(methodId),
    });
    if (amount != null) params.append('amount_declared', String(amount));
    if (reference) params.append('reference_text', reference);
    const { data } = await api.post<{ data: unknown }>(
      `/payments/submit?${params}`,
      formData
    );
    return data.data;
  },
};
