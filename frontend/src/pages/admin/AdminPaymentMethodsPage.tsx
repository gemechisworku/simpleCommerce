import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { PaymentMethod } from '../../types';

const PAYMENT_TYPES = ['BANK_TRANSFER', 'MOBILE_MONEY', 'CASH'] as const;

export function AdminPaymentMethodsPage() {
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingMethod, setEditingMethod] = useState<PaymentMethod | null>(null);
  const [form, setForm] = useState({
    type: 'BANK_TRANSFER' as string,
    name: '',
    account_identifier: '',
    account_holder: '',
    instructions: '',
    is_active: true,
    sort_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    adminService.listPaymentMethods(false).then(setMethods).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditingMethod(null);
    setForm({
      type: 'BANK_TRANSFER',
      name: '',
      account_identifier: '',
      account_holder: '',
      instructions: '',
      is_active: true,
      sort_order: 0,
    });
    setShowForm(true);
    setError('');
  };

  const openEdit = (m: PaymentMethod) => {
    setEditingMethod(m);
    setForm({
      type: m.type ?? 'BANK_TRANSFER',
      name: m.name,
      account_identifier: m.account_identifier,
      account_holder: m.account_holder,
      instructions: m.instructions ?? '',
      is_active: m.is_active ?? true,
      sort_order: m.sort_order ?? 0,
    });
    setShowForm(true);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      if (editingMethod) {
        await adminService.updatePaymentMethod(editingMethod.id, {
          name: form.name,
          account_identifier: form.account_identifier,
          account_holder: form.account_holder,
          instructions: form.instructions || undefined,
          is_active: form.is_active,
          sort_order: form.sort_order,
        });
      } else {
        await adminService.createPaymentMethod({
          type: form.type,
          name: form.name,
          account_identifier: form.account_identifier,
          account_holder: form.account_holder,
          instructions: form.instructions || undefined,
          is_active: form.is_active,
          sort_order: form.sort_order,
        });
      }
      setShowForm(false);
      setEditingMethod(null);
      load();
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message
        : 'Failed to save';
      setError(String(msg || 'Failed to save'));
    } finally {
      setSaving(false);
    }
  };

  const inputClass = "w-full rounded-lg border border-stroke bg-transparent px-4 py-2.5 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white";
  const labelClass = "mb-1.5 block text-sm font-medium text-black dark:text-white";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black dark:text-white">Payment Methods</h2>
          <p className="mt-1 text-body dark:text-body-dark">Bank accounts and payment options for customers</p>
        </div>
        <button type="button" onClick={openCreate} className="rounded-lg bg-primary px-5 py-2.5 font-medium text-white hover:bg-primary-dark">+ New Method</button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => { setShowForm(false); setEditingMethod(null); }}>
          <div className="w-full max-w-md rounded-lg border border-stroke bg-white p-6 shadow-xl dark:border-strokedark dark:bg-meta-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-black dark:text-white">{editingMethod ? 'Edit Payment Method' : 'Create Payment Method'}</h3>
            {error && <p className="mt-2 text-sm text-danger">{error}</p>}
            <form onSubmit={handleSubmit} className="mt-4 space-y-4">
              {!editingMethod && (
                <div>
                  <label className={labelClass}>Type *</label>
                  <select value={form.type} onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))} required className={inputClass}>
                    {PAYMENT_TYPES.map((t) => (
                      <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
                    ))}
                  </select>
                </div>
              )}
              <div><label className={labelClass}>Name *</label><input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required placeholder="e.g. CBE Bank" className={inputClass} /></div>
              <div><label className={labelClass}>Account / Identifier *</label><input value={form.account_identifier} onChange={(e) => setForm((f) => ({ ...f, account_identifier: e.target.value }))} required placeholder="Account number or phone" className={inputClass} /></div>
              <div><label className={labelClass}>Account Holder *</label><input value={form.account_holder} onChange={(e) => setForm((f) => ({ ...f, account_holder: e.target.value }))} required placeholder="Name on account" className={inputClass} /></div>
              <div><label className={labelClass}>Instructions</label><textarea value={form.instructions} onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))} rows={2} placeholder="Transfer instructions" className={inputClass} /></div>
              <div><label className={labelClass}>Sort order</label><input type="number" min={0} value={form.sort_order} onChange={(e) => setForm((f) => ({ ...f, sort_order: parseInt(e.target.value, 10) || 0 }))} className={inputClass} /></div>
              <label className="flex items-center gap-2"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))} className="rounded border-stroke" /><span className="text-sm text-black dark:text-white">Active</span></label>
              <div className="flex gap-2 pt-2">
                <button type="submit" className="rounded-lg bg-primary px-4 py-2 font-medium text-white hover:bg-primary-dark disabled:opacity-50" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
                <button type="button" className="rounded-lg border border-stroke px-4 py-2 font-medium hover:bg-gray-1 dark:border-strokedark dark:hover:bg-white/5" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16"><div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div></div>
      ) : methods.length === 0 ? (
        <div className="rounded-lg border border-stroke bg-white p-12 text-center dark:border-strokedark dark:bg-meta-4"><p className="text-body dark:text-body-dark">No payment methods.</p></div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {methods.map((m) => (
            <div key={m.id} className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
              <h3 className="font-semibold text-black dark:text-white">{m.name}</h3>
              <p className="mt-1 text-sm text-body dark:text-body-dark">{m.type?.replace(/_/g, ' ') ?? '—'} · {m.account_identifier}</p>
              <p className="text-sm text-body dark:text-body-dark">{m.account_holder}</p>
              <div className="mt-4"><button type="button" onClick={() => openEdit(m)} className="rounded-lg border border-stroke px-3 py-1.5 text-sm font-medium hover:bg-gray-1 dark:border-strokedark dark:hover:bg-white/5">Edit</button></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
