import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { paymentService } from '../services/paymentService';
import { Order, PaymentMethod } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';

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

  if (!order) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-bold text-black dark:text-white">Upload payment for {order.order_number}</h1>
      {order.payment_review_note && (
        <div className="rounded-lg border border-warning/50 bg-warning/10 p-4">
          <h2 className="mb-1 text-sm font-semibold text-black dark:text-white">Message from store</h2>
          <p className="text-sm text-black dark:text-white">{order.payment_review_note}</p>
        </div>
      )}
      <div className="rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-4">
        <p className="font-medium text-black dark:text-white"><strong>Total:</strong> ETB {order.total}</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Payment method *</label>
          <select value={methodId} onChange={(e) => setMethodId(Number(e.target.value))} required className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white">
            {methods.map((m) => (
              <option key={m.id} value={m.id}>{m.name} - {m.account_identifier}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Payment document (image or PDF) *</label>
          <input type="file" accept="image/jpeg,image/png,image/jpg,application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} required className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white file:mr-2 file:rounded file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-white" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Amount paid (optional)</label>
          <input type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder={order.total} className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white" />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Reference / Transaction ID (optional)</label>
          <input type="text" value={reference} onChange={(e) => setReference(e.target.value)} className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white" />
        </div>
        {error && <p className="text-sm text-danger">{error}</p>}
        <button type="submit" disabled={loading} className="w-full rounded-lg bg-primary py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50">
          {loading ? 'Submitting...' : 'Submit payment'}
        </button>
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
