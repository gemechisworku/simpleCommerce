import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { orderService } from '../services/orderService';
import { deliveryZoneService } from '../services/deliveryZoneService';
import { DeliveryZone } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';
import './CheckoutPage.css';

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
    if (!form.delivery_zone_id || !form.delivery_address || !form.recipient_name || !form.recipient_phone) {
      setError('Please fill all required fields');
      return;
    }
    setLoading(true);
    try {
      const order = await orderService.create({
        items: items.map((i) => ({ variant_id: i.variant_id, quantity: i.quantity })),
        delivery_zone_id: form.delivery_zone_id,
        delivery_address: form.delivery_address,
        recipient_name: form.recipient_name,
        recipient_phone: form.recipient_phone,
        delivery_instructions: form.delivery_instructions || undefined,
      });
      clearCart();
      navigate(`/orders/${order.id}/payment`);
    } catch (err: unknown) {
      const res = err && typeof err === 'object' && 'response' in err ? (err as { response?: { data?: { error?: { message?: string } } } }).response : undefined;
      setError(res?.data?.error?.message || 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0 && !loading) {
    return (
      <div className="checkout-page">
        <h1>Your cart is empty</h1>
        <button onClick={() => navigate('/')}>Continue shopping</button>
      </div>
    );
  }

  return (
    <div className="checkout-page">
      <h1>Checkout</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Delivery zone *</label>
          <select value={form.delivery_zone_id} onChange={(e) => setForm({ ...form, delivery_zone_id: Number(e.target.value) })} required>
            <option value={0}>Select zone</option>
            {zones.map((z) => (
              <option key={z.id} value={z.id}>{z.name} - ETB {z.fee} ({z.eta_min_days}-{z.eta_max_days} days)</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Delivery address *</label>
          <textarea value={form.delivery_address} onChange={(e) => setForm({ ...form, delivery_address: e.target.value })} required rows={3} />
        </div>
        <div className="form-group">
          <label>Recipient name *</label>
          <input type="text" value={form.recipient_name} onChange={(e) => setForm({ ...form, recipient_name: e.target.value })} required />
        </div>
        <div className="form-group">
          <label>Recipient phone *</label>
          <input type="tel" value={form.recipient_phone} onChange={(e) => setForm({ ...form, recipient_phone: e.target.value })} required />
        </div>
        <div className="form-group">
          <label>Delivery instructions (optional)</label>
          <textarea value={form.delivery_instructions} onChange={(e) => setForm({ ...form, delivery_instructions: e.target.value })} rows={2} />
        </div>
        <div className="order-summary"><strong>Order total: ETB {getCartTotal().toFixed(2)}</strong></div>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>{loading ? 'Placing order...' : 'Place order'}</button>
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
