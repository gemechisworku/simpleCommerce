import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { DeliveryZone } from '../../types';

const formInputClass = "w-full rounded-lg border border-stroke bg-transparent px-4 py-2.5 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white";
const formLabelClass = "mb-1.5 block text-sm font-medium text-black dark:text-white";
const btnPrimary = "rounded-lg bg-primary px-4 py-2 font-medium text-white hover:bg-primary-dark disabled:opacity-50";
const btnSecondary = "rounded-lg border border-stroke px-4 py-2 font-medium text-black hover:bg-gray-1 dark:border-strokedark dark:text-white dark:hover:bg-white/5";

export function AdminDeliveryZonesPage() {
  const [zones, setZones] = useState<DeliveryZone[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<DeliveryZone | null>(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
    fee: '',
    eta_min_days: 1,
    eta_max_days: 2,
    is_active: true,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    adminService.listDeliveryZones(false).then(setZones).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', description: '', fee: '', eta_min_days: 1, eta_max_days: 2, is_active: true });
    setShowForm(true);
    setError('');
  };

  const openEdit = (z: DeliveryZone) => {
    setEditing(z);
    setForm({
      name: z.name,
      description: z.description || '',
      fee: z.fee,
      eta_min_days: z.eta_min_days,
      eta_max_days: z.eta_max_days,
      is_active: z.is_active,
    });
    setShowForm(true);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    const fee = parseFloat(form.fee);
    if (isNaN(fee) || fee < 0) {
      setError('Invalid fee');
      setSaving(false);
      return;
    }
    if (form.eta_max_days < form.eta_min_days) {
      setError('ETA max must be >= ETA min');
      setSaving(false);
      return;
    }
    try {
      if (editing) {
        await adminService.updateDeliveryZone(editing.id, {
          name: form.name,
          description: form.description || undefined,
          fee: String(fee),
          eta_min_days: form.eta_min_days,
          eta_max_days: form.eta_max_days,
          is_active: form.is_active,
        });
      } else {
        await adminService.createDeliveryZone({
          name: form.name,
          description: form.description || undefined,
          fee: String(fee),
          eta_min_days: form.eta_min_days,
          eta_max_days: form.eta_max_days,
          is_active: form.is_active,
        });
      }
      setShowForm(false);
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
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black dark:text-white">Delivery Zones</h2>
          <p className="mt-1 text-body dark:text-body-dark">Configure delivery areas, fees and ETA</p>
        </div>
        <button type="button" onClick={openCreate} className={btnPrimary}>+ New Zone</button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setShowForm(false)}>
          <div className="w-full max-w-md rounded-lg border border-stroke bg-white p-6 shadow-xl dark:border-strokedark dark:bg-meta-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-black dark:text-white">{editing ? 'Edit Zone' : 'Create Zone'}</h3>
            {error && <p className="mt-2 text-sm text-danger">{error}</p>}
            <form onSubmit={handleSubmit} className="mt-4 space-y-4">
              <div>
                <label className={formLabelClass}>Name *</label>
                <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required className={formInputClass} />
              </div>
              <div>
                <label className={formLabelClass}>Description</label>
                <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={2} className={formInputClass} />
              </div>
              <div>
                <label className={formLabelClass}>Fee (ETB) *</label>
                <input type="number" value={form.fee} onChange={(e) => setForm((f) => ({ ...f, fee: e.target.value }))} min={0} step="0.01" required className={formInputClass} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={formLabelClass}>ETA Min (days)</label>
                  <input type="number" value={form.eta_min_days} onChange={(e) => setForm((f) => ({ ...f, eta_min_days: parseInt(e.target.value, 10) || 0 }))} min={0} className={formInputClass} />
                </div>
                <div>
                  <label className={formLabelClass}>ETA Max (days)</label>
                  <input type="number" value={form.eta_max_days} onChange={(e) => setForm((f) => ({ ...f, eta_max_days: parseInt(e.target.value, 10) || 1 }))} min={1} className={formInputClass} />
                </div>
              </div>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={form.is_active} onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))} className="rounded border-stroke" />
                <span className="text-sm text-black dark:text-white">Active</span>
              </label>
              <div className="flex gap-2 pt-2">
                <button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
                <button type="button" className={btnSecondary} onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div>
        </div>
      ) : zones.length === 0 ? (
        <div className="rounded-lg border border-stroke bg-white p-12 text-center dark:border-strokedark dark:bg-meta-4">
          <p className="text-body dark:text-body-dark">No delivery zones.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {zones.map((z) => (
            <div key={z.id} className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
              <h3 className="font-semibold text-black dark:text-white">{z.name}</h3>
              <p className="mt-1 text-sm text-body dark:text-body-dark">Fee: ETB {z.fee} · ETA: {z.eta_min_days}-{z.eta_max_days} days</p>
              <span className={`mt-2 inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${z.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>{z.is_active ? 'Active' : 'Inactive'}</span>
              <div className="mt-4">
                <button type="button" onClick={() => openEdit(z)} className={btnSecondary}>Edit</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
