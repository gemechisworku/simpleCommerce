import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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

export function AdminOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    adminService.listOrders({ page }).then((res) => {
      if (!cancelled) {
        setOrders(res.data);
        setTotalPages(res.meta.total_pages);
      }
      setLoading(false);
    }).catch(() => setLoading(false));
    return () => { cancelled = true; };
  }, [page]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black dark:text-white">Orders</h2>
          <p className="mt-1 text-body dark:text-body-dark">Manage and view all orders</p>
        </div>
      </div>

      <div className="rounded-lg border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-meta-4">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div>
          </div>
        ) : orders.length === 0 ? (
          <p className="p-8 text-body dark:text-body-dark">No orders.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-stroke text-left dark:border-strokedark">
                  <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Order #</th>
                  <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Status</th>
                  <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Total</th>
                  <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Date</th>
                  <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Action</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id} className="border-b border-stroke transition hover:bg-gray-1/50 dark:border-strokedark dark:hover:bg-white/5">
                    <td className="px-6 py-4 font-medium text-black dark:text-white">{o.order_number}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusBadge(o.status)}`}>
                        {o.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-body dark:text-body-dark">ETB {o.total}</td>
                    <td className="px-6 py-4 text-body dark:text-body-dark">{new Date(o.created_at).toLocaleDateString()}</td>
                    <td className="px-6 py-4">
                      <Link to={`/admin/orders/${o.id}`} className="font-medium text-primary hover:underline">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-stroke px-6 py-4 dark:border-strokedark">
            <p className="text-sm text-body dark:text-body-dark">Page {page} of {totalPages}</p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-lg border border-stroke px-4 py-2 text-sm font-medium text-black hover:bg-gray-1 disabled:opacity-50 dark:border-strokedark dark:text-white dark:hover:bg-white/5"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="rounded-lg border border-stroke px-4 py-2 text-sm font-medium text-black hover:bg-gray-1 disabled:opacity-50 dark:border-strokedark dark:text-white dark:hover:bg-white/5"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
