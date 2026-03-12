import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { resolveImageUrl } from '../../constants/api';

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
    if (actionModal.action === 'reject' && (!note.trim() || note.length < 10)) {
      alert('Rejection reason must be at least 10 characters');
      return;
    }
    setSubmitting(true);
    try {
      if (actionModal.action === 'approve') {
        await adminService.approvePayment(actionModal.payment.id, note);
      } else if (actionModal.action === 'reject') {
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
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-black dark:text-white">Payment queue</h2>
        <p className="mt-1 text-body dark:text-body-dark">Review and approve pending payments</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div>
        </div>
      ) : payments.length === 0 ? (
        <div className="rounded-lg border border-stroke bg-white p-12 text-center dark:border-strokedark dark:bg-meta-4">
          <p className="text-body dark:text-body-dark">No pending payments.</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {payments.map((p) => (
            <div
              key={p.id}
              className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4"
            >
              <div className="flex flex-col gap-4 sm:flex-row">
                {p.screenshot_url && (
                  <div className="shrink-0">
                    <img
                      src={resolveImageUrl(p.screenshot_url) ?? p.screenshot_url}
                      alt="Payment screenshot"
                      className="max-h-48 rounded-lg border border-stroke object-cover dark:border-strokedark"
                    />
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-black dark:text-white">Order #{p.order_id}</p>
                  <p className="text-sm text-body dark:text-body-dark">{p.amount_declared ? `ETB ${p.amount_declared}` : '—'}</p>
                  <p className="text-sm text-body dark:text-body-dark">{new Date(p.created_at).toLocaleString()}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setActionModal({ payment: p, action: 'approve' })}
                      className="rounded-lg bg-green-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-700"
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      onClick={() => setActionModal({ payment: p, action: 'reject' })}
                      className="rounded-lg bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
                    >
                      Reject
                    </button>
                    <button
                      type="button"
                      onClick={() => setActionModal({ payment: p, action: 'resubmit' })}
                      className="rounded-lg border border-stroke px-3 py-1.5 text-sm font-medium hover:bg-gray-1 dark:border-strokedark dark:hover:bg-white/5"
                    >
                      Request Resubmission
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {actionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setActionModal(null)}>
          <div className="w-full max-w-md rounded-lg border border-stroke bg-white p-6 shadow-xl dark:border-strokedark dark:bg-meta-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-black dark:text-white">
              {actionModal.action === 'approve' && 'Approve Payment'}
              {actionModal.action === 'reject' && 'Reject Payment'}
              {actionModal.action === 'resubmit' && 'Request Resubmission'}
            </h3>
            <p className="mt-2 text-body dark:text-body-dark">Order #{actionModal.payment.order_id}</p>
            <div className="mt-4">
              <label className="block text-sm font-medium text-black dark:text-white">
                {actionModal.action === 'reject' ? 'Reason (min 10 chars) *' : 'Note (optional)'}
              </label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={3}
                required={actionModal.action === 'reject'}
                className="mt-1 w-full rounded-lg border border-stroke bg-transparent px-4 py-2 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white"
              />
            </div>
            <div className="mt-6 flex gap-2">
              <button
                type="button"
                onClick={handleAction}
                disabled={submitting}
                className="rounded-lg bg-primary px-4 py-2 font-medium text-white hover:bg-primary-dark disabled:opacity-50"
              >
                {submitting ? 'Processing...' : 'Confirm'}
              </button>
              <button
                type="button"
                onClick={() => setActionModal(null)}
                className="rounded-lg border border-stroke px-4 py-2 font-medium hover:bg-gray-1 dark:border-strokedark dark:hover:bg-white/5"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-body dark:text-body-dark">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <button onClick={() => setPage((x) => Math.max(1, x - 1))} disabled={page <= 1} className="rounded-lg border border-stroke px-4 py-2 text-sm font-medium hover:bg-gray-1 disabled:opacity-50 dark:border-strokedark dark:hover:bg-white/5">Previous</button>
            <button onClick={() => setPage((x) => Math.min(totalPages, x + 1))} disabled={page >= totalPages} className="rounded-lg border border-stroke px-4 py-2 text-sm font-medium hover:bg-gray-1 disabled:opacity-50 dark:border-strokedark dark:hover:bg-white/5">Next</button>
          </div>
        </div>
      )}
    </div>
  );
}
