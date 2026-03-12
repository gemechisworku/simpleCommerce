import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { orderService } from '../services/orderService';
import { deliveryZoneService } from '../services/deliveryZoneService';
import { DeliveryZone } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';

function CheckoutPageInner() {
  const { items, getCartTotal, clearCart } = useCart();
  const navigate = useNavigate();
  const [zones, setZones] = useState<DeliveryZone[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    delivery_zone_id: 0,
    delivery_address: '',
    recipient_name: '',
    recipient_phone: '',
    delivery_instructions: '',
  });

  useEffect(() => {
    deliveryZoneService.list().then((z) => setZones(z));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (items.length === 0) {
      setError('Cart is empty');
      return;
    }
    if (!form.delivery_zone_id || form.delivery_zone_id <= 0) {
      setError('Please select a delivery zone');
      return;
    }
    const addr = form.delivery_address.trim();
    const name = form.recipient_name.trim();
    const phone = form.recipient_phone.trim();
    if (!addr || !name || !phone) {
      setError('Please fill all required fields');
      return;
    }
    if (addr.length < 10) {
      setError('Delivery address must be at least 10 characters');
      return;
    }
    if (name.length > 100) {
      setError('Recipient name must be 100 characters or less');
      return;
    }
    if (phone.length > 20) {
      setError('Recipient phone must be 20 characters or less');
      return;
    }
    setLoading(true);
    try {
      const order = await orderService.create({
        items: items.map((i) => ({
          product_id: i.product_id,
          variant_id: i.variant_id,
          quantity: i.quantity,
        })),
        delivery_zone_id: form.delivery_zone_id,
        delivery_address: addr,
        recipient_name: name,
        recipient_phone: phone,
        delivery_instructions: form.delivery_instructions?.trim() || undefined,
      });
      clearCart();
      navigate(`/orders/${order.id}/payment`);
    } catch (err: unknown) {
      const res = err && typeof err === 'object' && 'response' in err ? (err as { response?: { status?: number; data?: { message?: string; error?: { message?: string }; detail?: Array<{ msg?: string; message?: string }> } } }).response : undefined;
      if (res?.status === 401) {
        setError('Session expired. Please log in again.');
        return;
      }
      const data = res?.data;
      let msg = data?.error?.message ?? data?.message;
      const detail = data?.detail;
      if (!msg && Array.isArray(detail) && detail.length > 0) {
        msg = detail.map((d: { msg?: string; message?: string }) => d.msg ?? d.message).filter(Boolean).join('. ') || undefined;
      }
      setError(msg || 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0 && !loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <h1 className="text-2xl font-bold text-black dark:text-white">Your cart is empty</h1>
        <button type="button" onClick={() => navigate('/')} className="mt-4 rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:opacity-90">Continue shopping</button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-bold text-black dark:text-white">Checkout</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Delivery zone *</label>
          <select
            value={form.delivery_zone_id}
            onChange={(e) => setForm({ ...form, delivery_zone_id: Number(e.target.value) })}
            required
            className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white"
          >
            <option value={0}>Select zone</option>
            {zones.map((z) => (
              <option key={z.id} value={z.id}>{z.name} - ETB {z.fee} ({z.eta_min_days}-{z.eta_max_days} days)</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Delivery address *</label>
          <textarea value={form.delivery_address} onChange={(e) => setForm({ ...form, delivery_address: e.target.value })} required rows={3} className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Recipient name *</label>
          <input type="text" value={form.recipient_name} onChange={(e) => setForm({ ...form, recipient_name: e.target.value })} required className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Recipient phone *</label>
          <input type="tel" value={form.recipient_phone} onChange={(e) => setForm({ ...form, recipient_phone: e.target.value })} required className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Delivery instructions (optional)</label>
          <textarea value={form.delivery_instructions} onChange={(e) => setForm({ ...form, delivery_instructions: e.target.value })} rows={2} className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white" />
        </div>
        <p className="text-lg font-semibold text-black dark:text-white">Order total: ETB {getCartTotal().toFixed(2)}</p>
        {error && <p className="text-sm text-danger">{error}</p>}
        <button type="submit" disabled={loading} className="w-full rounded-lg bg-primary py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50">
          {loading ? 'Placing order...' : 'Place order'}
        </button>
      </form>
    </div>
  );
}

export function CheckoutPage() {
  return (
    <ProtectedRoute>
      <CheckoutPageInner />
    </ProtectedRoute>
  );
}
