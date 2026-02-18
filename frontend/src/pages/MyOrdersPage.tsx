import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { Order } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';
import './MyOrdersPage.css';

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

  return (
    <div className="my-orders-page">
      <h1>My Orders</h1>
      {loading ? (
        <p>Loading...</p>
      ) : orders.length === 0 ? (
        <p>No orders yet.</p>
      ) : (
        <div className="orders-list">
          {orders.map((o) => (
            <Link key={o.id} to={`/orders/${o.id}`} className="order-card">
              <div className="order-header">
                <span className="order-number">{o.order_number}</span>
                <span className={`status status-${o.status.toLowerCase().replace('_', '-')}`}>{o.status}</span>
              </div>
              <div className="order-meta">
                <span>ETB {o.total}</span>
                <span>{new Date(o.created_at).toLocaleDateString()}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>Previous</button>
          <span>Page {page} of {totalPages}</span>
          <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>Next</button>
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
