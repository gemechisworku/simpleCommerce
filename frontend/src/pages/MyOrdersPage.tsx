import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { Order } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';

function MyOrdersPageInner() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    orderService.listMy({ page }).then((res) => {
      if (!cancelled) {
        setOrders(res.data);
        setTotalPages(res.meta.total_pages);
      }
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, [page]);

  const statusClass = (status: string) => {
    const s = status.toLowerCase().replace('_', '-');
    if (s.includes('paid') || s.includes('delivered')) return 'bg-success/20 text-success';
    if (s.includes('pending') || s.includes('processing')) return 'bg-warning/20 text-warning';
    if (s.includes('rejected') || s.includes('cancelled')) return 'bg-danger/20 text-danger';
    return 'bg-gray-1 dark:bg-white/10 text-black dark:text-white';
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-black dark:text-white">My Orders</h1>
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent" />
        </div>
      ) : orders.length === 0 ? (
        <p className="text-black dark:text-white">No orders yet.</p>
      ) : (
        <div className="space-y-3">
          {orders.map((o) => (
            <Link key={o.id} to={`/orders/${o.id}`} className="block rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-4 text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-medium">{o.order_number}</span>
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusClass(o.status)}`}>{o.status}</span>
              </div>
              <div className="mt-2 flex flex-wrap gap-4 text-sm text-black dark:text-white">
                <span>ETB {o.total}</span>
                <span>{new Date(o.created_at).toLocaleDateString()}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
      {totalPages > 1 && (
        <div className="flex flex-wrap items-center justify-center gap-4 py-4">
          <button type="button" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1} className="rounded-lg border border-stroke dark:border-strokedark px-4 py-2 text-black dark:text-white disabled:opacity-50">Previous</button>
          <span className="text-black dark:text-white">Page {page} of {totalPages}</span>
          <button type="button" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages} className="rounded-lg border border-stroke dark:border-strokedark px-4 py-2 text-black dark:text-white disabled:opacity-50">Next</button>
        </div>
      )}
    </div>
  );
}

export function MyOrdersPage() {
  return (
    <ProtectedRoute>
      <MyOrdersPageInner />
    </ProtectedRoute>
  );
}
