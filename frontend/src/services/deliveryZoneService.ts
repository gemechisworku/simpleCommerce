import api from './api';
import { DeliveryZone } from '../types';

export const deliveryZoneService = {
  async list() {
    const { data } = await api.get<{ data: DeliveryZone[] }>('/admin/delivery-zones/public/list');
    return data.data;
  },
};
