import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Order } from '../../types';

const statusBadgeClass: Record<string, string> = {
  PENDING_PAYMENT: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  PAYMENT_SUBMITTED: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  PAID: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
  PACKING: 'bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-400',
  DISPATCHED: 'bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-400',
  DELIVERED: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  CANCELLED: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  PAYMENT_REJECTED: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
};

function getStatusBadge(status: string) {
  return statusBadgeClass[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
}

export function AdminOrderDetailPage() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = Number(orderId);
    if (!id) return;
    adminService.getOrder(id).then(setOrder).catch(() => navigate('/admin/orders')).finally(() => setLoading(false));
  }, [orderId, navigate]);

  if (loading || !order) {
    return (
      <div className="flex items-center justify-center py-16">
        {loading ? <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div> : <p className="text-black dark:text-white">Order not found.</p>}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button type="button" onClick={() => navigate(-1)} className="rounded-lg border border-stroke px-3 py-2 text-sm font-medium text-black hover:bg-gray-1 dark:border-strokedark dark:text-white dark:hover:bg-white/5">← Back</button>
        <h2 className="text-2xl font-bold text-black dark:text-white">Order {order.order_number}</h2>
        <span className={`inline-flex rounded-full px-3 py-1 text-sm font-medium ${getStatusBadge(order.status)}`}>{order.status.replace(/_/g, ' ')}</span>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <h3 className="mb-4 text-lg font-semibold text-black dark:text-white">Order details</h3>
          <dl className="space-y-2 text-sm">
            <div><dt className="text-body dark:text-body-dark">Total</dt><dd className="font-medium text-black dark:text-white">ETB {order.total}</dd></div>
            <div><dt className="text-body dark:text-body-dark">Delivery address</dt><dd className="text-black dark:text-white">{order.delivery_address}</dd></div>
            <div><dt className="text-body dark:text-body-dark">Recipient</dt><dd className="text-black dark:text-white">{order.recipient_name} · {order.recipient_phone}</dd></div>
            {order.delivery_instructions && <div><dt className="text-body dark:text-body-dark">Instructions</dt><dd className="text-black dark:text-white">{order.delivery_instructions}</dd></div>}
          </dl>
        </div>

        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <h3 className="mb-4 text-lg font-semibold text-black dark:text-white">Items</h3>
          <ul className="space-y-3">
            {order.items.map((i) => (
              <li key={i.id} className="flex justify-between border-b border-stroke pb-3 last:border-0 dark:border-strokedark">
                <span className="text-black dark:text-white">{i.product_name}{i.variant_label ? ` · ${i.variant_label}` : ''} × {i.quantity}</span>
                <span className="text-body dark:text-body-dark">ETB {i.line_total}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 font-medium text-black dark:text-white">Subtotal: ETB {order.subtotal} · Delivery: ETB {order.delivery_fee}</p>
        </div>
      </div>
    </div>
  );
}
