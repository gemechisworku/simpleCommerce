import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { resolveImageUrl } from '../../constants/api';
import './AdminPaymentsPage.css';

interface Payment {
  id: number;
  order_id: number;
  status: string;
  amount_declared?: string | null;
  screenshot_url?: string;
  created_at: string;
}

export function AdminPaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [actionModal, setActionModal] = useState<{ payment: Payment; action: 'approve' | 'reject' | 'resubmit' } | null>(null);
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = () => {
    setLoading(true);
    adminService.listPaymentQueue({ page }).then((res) => {
      setPayments(res.data);
      setTotalPages(res.meta.total_pages);
    }).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [page]);

  const handleAction = async () => {
    if (!actionModal) return;
    setSubmitting(true);
    try {
      if (actionModal.action === 'approve') {
        await adminService.approvePayment(actionModal.payment.id, note);
      } else if (actionModal.action === 'reject') {
        if (!note.trim() || note.length < 10) {
          alert('Rejection reason must be at least 10 characters');
          setSubmitting(false);
          return;
        }
        await adminService.rejectPayment(actionModal.payment.id, note);
      } else {
        await adminService.requestPaymentResubmit(actionModal.payment.id, note);
      }
      setActionModal(null);
      setNote('');
      load();
    } catch {
      alert('Action failed');
    } finally {
      setSubmitting(false);
    }
  };

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
            <div key={p.id} className="payment-card">
              <div className="payment-info">
                <span>Order #{p.order_id}</span>
                <span>{p.status}</span>
                <span>{p.amount_declared ? `ETB ${p.amount_declared}` : '-'}</span>
                <span>{new Date(p.created_at).toLocaleString()}</span>
              </div>
              {p.screenshot_url && (
                <div className="payment-screenshot">
                  <img src={resolveImageUrl(p.screenshot_url) ?? p.screenshot_url} alt="Payment screenshot" />
                </div>
              )}
              <div className="payment-actions">
                <button className="btn-approve" onClick={() => setActionModal({ payment: p, action: 'approve' })}>Approve</button>
                <button className="btn-reject" onClick={() => setActionModal({ payment: p, action: 'reject' })}>Reject</button>
                <button className="btn-resubmit" onClick={() => setActionModal({ payment: p, action: 'resubmit' })}>Request Resubmission</button>
              </div>
            </div>
          ))}
        </div>
      )}
      {actionModal && (
        <div className="modal-overlay" onClick={() => setActionModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>
              {actionModal.action === 'approve' && 'Approve Payment'}
              {actionModal.action === 'reject' && 'Reject Payment'}
              {actionModal.action === 'resubmit' && 'Request Resubmission'}
            </h2>
            <p>Order #{actionModal.payment.order_id}</p>
            <div className="form-group">
              <label>{actionModal.action === 'reject' ? 'Reason (min 10 chars) *' : 'Note (optional)'}</label>
              <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={3} required={actionModal.action === 'reject'} />
            </div>
            <div className="form-actions">
              <button className="btn-primary" onClick={handleAction} disabled={submitting}>
                {submitting ? 'Processing...' : 'Confirm'}
              </button>
              <button className="btn-secondary" onClick={() => setActionModal(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => setPage((x) => Math.max(1, x - 1))} disabled={page <= 1}>Previous</button>
          <span>Page {page} of {totalPages}</span>
          <button onClick={() => setPage((x) => Math.min(totalPages, x + 1))} disabled={page >= totalPages}>Next</button>
        </div>
      )}
    </div>
  );
}
