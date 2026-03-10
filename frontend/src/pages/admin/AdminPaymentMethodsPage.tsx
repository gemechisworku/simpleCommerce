import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { PaymentMethod } from '../../types';
import './AdminCrudPage.css';
import './AdminPaymentMethodsPage.css';

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

  return (
    <div className="admin-crud-page admin-payment-methods-page">
      <div className="page-header">
        <h1>Payment Methods</h1>
        <button className="btn-primary" onClick={openCreate}>+ New Method</button>
      </div>
      {showForm && (
        <div className="modal-overlay" onClick={() => { setShowForm(false); setEditingMethod(null); }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{editingMethod ? 'Edit Payment Method' : 'Create Payment Method'}</h2>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
              {!editingMethod && (
                <div className="form-group">
                  <label>Type *</label>
                  <select value={form.type} onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))} required>
                    {PAYMENT_TYPES.map((t) => (
                      <option key={t} value={t}>{t.replace('_', ' ')}</option>
                    ))}
                  </select>
                </div>
              )}
              <div className="form-group">
                <label>Name *</label>
                <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required placeholder="e.g. CBE Bank" />
              </div>
              <div className="form-group">
                <label>Account / Identifier *</label>
                <input value={form.account_identifier} onChange={(e) => setForm((f) => ({ ...f, account_identifier: e.target.value }))} required placeholder="Account number or phone" />
              </div>
              <div className="form-group">
                <label>Account Holder *</label>
                <input value={form.account_holder} onChange={(e) => setForm((f) => ({ ...f, account_holder: e.target.value }))} required placeholder="Name on account" />
              </div>
              <div className="form-group">
                <label>Instructions</label>
                <textarea value={form.instructions} onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))} rows={2} placeholder="Transfer instructions" />
              </div>
              <div className="form-group">
                <label>Sort order</label>
                <input type="number" min={0} value={form.sort_order} onChange={(e) => setForm((f) => ({ ...f, sort_order: parseInt(e.target.value, 10) || 0 }))} />
              </div>
              <label><input type="checkbox" checked={form.is_active} onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))} /> Active</label>
              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
      {loading ? (
        <p>Loading...</p>
      ) : methods.length === 0 ? (
        <p>No payment methods.</p>
      ) : (
        <div className="crud-list">
          {methods.map((m) => (
            <div key={m.id} className="crud-card">
              <div className="card-body">
                <h3>{m.name}</h3>
                <p className="card-meta">{m.type?.replace('_', ' ') ?? '—'} · {m.account_identifier}</p>
                <p className="card-meta">{m.account_holder}</p>
                <button type="button" className="btn-secondary" onClick={() => openEdit(m)}>Edit</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
