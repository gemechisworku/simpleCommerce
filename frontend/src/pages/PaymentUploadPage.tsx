import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { paymentService } from '../services/paymentService';
import { Order, PaymentMethod } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';
import './PaymentUploadPage.css';

function PaymentUploadPageInner() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [methodId, setMethodId] = useState(0);
  const [amount, setAmount] = useState('');
  const [reference, setReference] = useState('');

  useEffect(() => {
    const id = Number(orderId);
    if (!id) return;
    Promise.all([
      orderService.getById(id),
      paymentService.listMethods(),
    ]).then(([o, m]) => {
      setOrder(o);
      setMethods(m);
      if (m[0]) setMethodId(m[0].id);
    }).catch(() => navigate('/orders'));
  }, [orderId, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!order || !file || !methodId) {
      setError('Please select a payment method and upload screenshot');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await paymentService.submit(
        order.id,
        methodId,
        file,
        amount ? parseFloat(amount) : undefined,
        reference || undefined
      );
      navigate(`/orders/${order.id}`);
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message
        : 'Failed to submit payment';
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  };

  if (!order) return <div className="payment-upload-page"><p>Loading...</p></div>;

  return (
    <div className="payment-upload-page">
      <h1>Upload payment for {order.order_number}</h1>
      <div className="order-summary-box">
        <p><strong>Total:</strong> ETB {order.total}</p>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Payment method *</label>
          <select value={methodId} onChange={(e) => setMethodId(Number(e.target.value))} required>
            {methods.map((m) => (
              <option key={m.id} value={m.id}>{m.name} - {m.account_identifier}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Screenshot *</label>
          <input type="file" accept="image/jpeg,image/png,image/jpg" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
        </div>
        <div className="form-group">
          <label>Amount paid (optional)</label>
          <input type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder={order.total} />
        </div>
        <div className="form-group">
          <label>Reference / Transaction ID (optional)</label>
          <input type="text" value={reference} onChange={(e) => setReference(e.target.value)} />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>{loading ? 'Submitting...' : 'Submit payment'}</button>
      </form>
    </div>
  );
}

export function PaymentUploadPage() {
  return (
    <ProtectedRoute>
      <PaymentUploadPageInner />
    </ProtectedRoute>
  );
}
