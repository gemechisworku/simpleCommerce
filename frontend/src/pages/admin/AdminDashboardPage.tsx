import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import './AdminDashboardPage.css';

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

  if (loading) return <p>Loading...</p>;
  if (!metrics) return <p>Failed to load dashboard.</p>;

  return (
    <div className="admin-dashboard">
      <h1>Dashboard</h1>
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-value">{metrics.orders_today}</span>
          <span className="metric-label">Orders today</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics.pending_payments_count}</span>
          <span className="metric-label">Pending payments</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">ETB {metrics.revenue_today.toFixed(2)}</span>
          <span className="metric-label">Revenue today</span>
        </div>
      </div>
      <div className="orders-by-status">
        <h2>Orders by status</h2>
        <ul>
          {Object.entries(metrics.orders_by_status).map(([status, count]) => (
            <li key={status}>{status}: {count}</li>
          ))}
        </ul>
      </div>
      <div className="recent-orders">
        <h2>Recent orders</h2>
        {metrics.recent_orders.length === 0 ? (
          <p>No recent orders.</p>
        ) : (
          <div className="orders-list">
            {metrics.recent_orders.map((o) => (
              <Link key={o.id} to={`/admin/orders/${o.id}`} className="order-row">
                <span>{o.order_number}</span>
                <span>{o.status}</span>
                <span>ETB {o.total}</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
