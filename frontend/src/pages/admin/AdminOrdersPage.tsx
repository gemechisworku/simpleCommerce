import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Order } from '../../types';
import './AdminOrdersPage.css';

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
    <div className="admin-orders-page">
      <h1>Orders</h1>
      {loading ? <p>Loading...</p> : orders.length === 0 ? <p>No orders.</p> : (
        <div className="orders-table">
          {orders.map((o) => (
            <Link key={o.id} to={`/admin/orders/${o.id}`} className="order-row">
              <span>{o.order_number}</span>
              <span>{o.status}</span>
              <span>ETB {o.total}</span>
              <span>{new Date(o.created_at).toLocaleDateString()}</span>
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
