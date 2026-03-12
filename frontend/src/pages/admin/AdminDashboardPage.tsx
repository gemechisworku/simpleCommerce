import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';

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

export function AdminDashboardPage() {
  const [metrics, setMetrics] = useState<{
    orders_today: number;
    pending_payments_count: number;
    orders_by_status: Record<string, number>;
    revenue_today: number;
    recent_orders: { id: number; order_number: string; status: string; total: string }[];
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService.getDashboard().then((m) => {
      setMetrics(m);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
          <p className="mt-4 text-body dark:text-body-dark">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="rounded-lg border border-stroke bg-white p-8 shadow-default dark:border-strokedark dark:bg-meta-4">
        <p className="text-danger">Failed to load dashboard.</p>
      </div>
    );
  }

  const statusEntries = Object.entries(metrics.orders_by_status);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-black dark:text-white">Dashboard</h2>
        <p className="mt-1 text-body dark:text-body-dark">Overview of your store</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-body dark:text-body-dark">Orders today</p>
              <p className="mt-2 text-2xl font-bold text-black dark:text-white">{metrics.orders_today}</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <span className="text-2xl">📦</span>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-body dark:text-body-dark">Pending payments</p>
              <p className="mt-2 text-2xl font-bold text-black dark:text-white">{metrics.pending_payments_count}</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-500/10">
              <span className="text-2xl">💳</span>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-body dark:text-body-dark">Revenue today</p>
              <p className="mt-2 text-2xl font-bold text-black dark:text-white">ETB {Number(metrics.revenue_today).toFixed(2)}</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
              <span className="text-2xl">💰</span>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-body dark:text-body-dark">Statuses</p>
              <p className="mt-2 text-xl font-bold text-black dark:text-white">{statusEntries.length} active</p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-violet-500/10">
              <span className="text-2xl">📊</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Orders by status */}
        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <h3 className="mb-4 text-lg font-semibold text-black dark:text-white">Orders by status</h3>
          {statusEntries.length === 0 ? (
            <p className="text-body dark:text-body-dark">No orders yet.</p>
          ) : (
            <ul className="space-y-2">
              {statusEntries.map(([status, count]) => (
                <li key={status} className="flex items-center justify-between rounded-lg bg-gray-1 px-4 py-2 dark:bg-meta-4">
                  <span className="font-medium text-black dark:text-white">{status.replace(/_/g, ' ')}</span>
                  <span className="rounded-full bg-primary/10 px-3 py-0.5 text-sm font-medium text-primary">{count}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Recent orders */}
        <div className="rounded-lg border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-meta-4">
          <div className="flex items-center justify-between border-b border-stroke px-6 py-4 dark:border-strokedark">
            <h3 className="text-lg font-semibold text-black dark:text-white">Recent orders</h3>
            <Link
              to="/admin/orders"
              className="text-sm font-medium text-primary hover:underline"
            >
              See all
            </Link>
          </div>
          <div className="overflow-x-auto">
            {metrics.recent_orders.length === 0 ? (
              <p className="p-6 text-body dark:text-body-dark">No recent orders.</p>
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-stroke text-left dark:border-strokedark">
                    <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Order</th>
                    <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Status</th>
                    <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Total</th>
                    <th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {metrics.recent_orders.map((o) => (
                    <tr key={o.id} className="border-b border-stroke transition hover:bg-gray-1/50 dark:border-strokedark dark:hover:bg-white/5">
                      <td className="px-6 py-4 font-medium text-black dark:text-white">{o.order_number}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusBadge(o.status)}`}>
                          {o.status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-body dark:text-body-dark">ETB {o.total}</td>
                      <td className="px-6 py-4">
                        <Link
                          to={`/admin/orders/${o.id}`}
                          className="text-primary hover:underline font-medium"
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
