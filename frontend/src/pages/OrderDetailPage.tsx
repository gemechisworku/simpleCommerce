import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { Order } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';

function OrderDetailPageInner() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = Number(orderId);
    if (!id) return;
    orderService.getById(id).then(setOrder).catch(() => navigate('/orders')).finally(() => setLoading(false));
  }, [orderId, navigate]);

  const canPay = order && ['PENDING_PAYMENT', 'PAYMENT_REJECTED', 'PAYMENT_RESUBMIT_REQUESTED'].includes(order.status);
  const canCancel = order && order.status === 'PENDING_PAYMENT';

  const statusClass = (status: string) => {
    const s = status.toLowerCase().replace(/_/g, '-');
    if (s.includes('paid') || s.includes('delivered')) return 'bg-success/20 text-success';
    if (s.includes('pending') || s.includes('processing')) return 'bg-warning/20 text-warning';
    if (s.includes('rejected') || s.includes('cancelled')) return 'bg-danger/20 text-danger';
    return 'bg-gray-1 dark:bg-white/10 text-black dark:text-white';
  };

  if (loading || !order) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        {loading ? <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent" /> : <p className="text-black dark:text-white">Order not found.</p>}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-black dark:text-white">Order {order.order_number}</h1>
      <p className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${statusClass(order.status)}`}>{order.status}</p>
      <div className="rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-4 space-y-2 text-black dark:text-white">
        <p><strong>Total:</strong> ETB {order.total}</p>
        <p><strong>Address:</strong> {order.delivery_address}</p>
        <p><strong>Recipient:</strong> {order.recipient_name} ({order.recipient_phone})</p>
      </div>
      <div>
        <h2 className="mb-2 text-lg font-semibold text-black dark:text-white">Items</h2>
        <div className="space-y-2">
          {order.items.map((i) => (
            <div key={i.id} className="flex flex-wrap justify-between gap-2 rounded-lg border border-stroke dark:border-strokedark p-3 text-black dark:text-white">
              <span>{i.product_name} {i.variant_label && `- ${i.variant_label}`}</span>
              <span className="text-sm">Qty: {i.quantity} × ETB {i.unit_price} = ETB {i.line_total}</span>
            </div>
          ))}
        </div>
      </div>
      {order.payment_review_note && (
        <div className="rounded-lg border border-warning/50 bg-warning/10 p-4">
          <h2 className="mb-1 text-sm font-semibold text-black dark:text-white">Message from store</h2>
          <p className="text-sm text-black dark:text-white">{order.payment_review_note}</p>
        </div>
      )}
      {order.status_history && order.status_history.length > 0 && (
        <div>
          <h2 className="mb-2 text-lg font-semibold text-black dark:text-white">Status history</h2>
          <div className="space-y-1 text-sm text-black dark:text-white">
            {order.status_history.map((h, idx) => (
              <p key={idx}>{h.new_status} — {new Date(h.created_at).toLocaleString()}</p>
            ))}
          </div>
        </div>
      )}
      <div className="flex flex-wrap gap-3">
        {canPay && <Link to={`/orders/${order.id}/payment`} className="rounded-lg bg-primary px-4 py-2.5 font-medium text-white hover:opacity-90">Upload payment</Link>}
        {canCancel && <button type="button" onClick={() => orderService.cancel(order.id).then(() => navigate('/orders'))} className="rounded-lg border border-stroke dark:border-strokedark px-4 py-2.5 font-medium text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10">Cancel order</button>}
      </div>
    </div>
  );
}

export function OrderDetailPage() {
  return (
    <ProtectedRoute>
      <OrderDetailPageInner />
    </ProtectedRoute>
  );
}
