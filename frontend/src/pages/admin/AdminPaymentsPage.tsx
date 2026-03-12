import React, { useState, useEffect, useCallback } from 'react';
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

function isPdfUrl(url: string): boolean {
  return url.toLowerCase().endsWith('.pdf');
}

export function AdminPaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [actionModal, setActionModal] = useState<{ payment: Payment; action: 'approve' | 'reject' | 'resubmit' } | null>(null);
  const [viewAttachment, setViewAttachment] = useState<Payment | null>(null);
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    adminService.listPaymentQueue({ page }).then((res) => {
      setPayments(res.data);
      setTotalPages(res.meta.total_pages);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [page]);

  useEffect(() => { load(); }, [load]);

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
                  <div className="shrink-0 flex flex-col gap-2">
                    {isPdfUrl(p.screenshot_url) ? (
                      <div className="flex max-h-48 min-h-[120px] w-40 items-center justify-center rounded-lg border border-stroke bg-gray-1 dark:border-strokedark dark:bg-white/5">
                        <span className="text-4xl text-body dark:text-body-dark">PDF</span>
                      </div>
                    ) : (
                      <img
                        src={resolveImageUrl(p.screenshot_url) ?? p.screenshot_url}
                        alt="Payment document"
                        className="max-h-48 rounded-lg border border-stroke object-cover dark:border-strokedark"
                      />
                    )}
                    <button
                      type="button"
                      onClick={() => setViewAttachment(p)}
                      className="rounded-lg border border-stroke px-2 py-1 text-xs font-medium text-black hover:bg-gray-1 dark:border-strokedark dark:text-white dark:hover:bg-white/10"
                    >
                      View attachment
                    </button>
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

      {viewAttachment?.screenshot_url && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={() => setViewAttachment(null)}>
          <div className="relative max-h-[90vh] max-w-4xl overflow-hidden rounded-lg bg-white dark:bg-meta-4 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <button type="button" onClick={() => setViewAttachment(null)} className="absolute right-2 top-2 z-10 rounded bg-black/50 p-1.5 text-white hover:bg-black/70">✕</button>
            {isPdfUrl(viewAttachment.screenshot_url) ? (
              <iframe
                title="Payment document"
                src={resolveImageUrl(viewAttachment.screenshot_url) ?? viewAttachment.screenshot_url}
                className="h-[85vh] w-full min-w-[320px]"
              />
            ) : (
              <img
                src={resolveImageUrl(viewAttachment.screenshot_url) ?? viewAttachment.screenshot_url}
                alt="Payment document"
                className="max-h-[85vh] max-w-full object-contain"
              />
            )}
          </div>
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
