import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import './AdminPaymentsPage.css';

interface Payment {
  id: number;
  order_id: number;
  status: string;
  amount_declared?: string;
  created_at: string;
}

export function AdminPaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api.get('/payments/queue', { params: { page } }).then((res) => {
      if (!cancelled) {
        setPayments(res.data.data);
        setTotalPages(res.data.meta.total_pages);
      }
      setLoading(false);
    }).catch(() => setLoading(false));
    return () => { cancelled = true; };
  }, [page]);

  return (
    <div className="admin-payments-page">
      <h1>Payment queue</h1>
      {loading ? (
        <p>Loading...</p>
      ) : payments.length === 0 ? (
        <p>No pending payments.</p>
      ) : (
        <div className="payments-list">
          {payments.map((p) => (
            <div key={p.id} className="payment-row">
              <span>Order #{p.order_id}</span>
              <span>{p.status}</span>
              <span>{p.amount_declared ? `ETB ${p.amount_declared}` : '-'}</span>
              <span>{new Date(p.created_at).toLocaleString()}</span>
            </div>
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
