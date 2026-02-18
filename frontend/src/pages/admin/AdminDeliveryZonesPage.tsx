import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { DeliveryZone } from '../../types';
import './AdminCrudPage.css';
import './AdminDeliveryZonesPage.css';

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
    <div className="admin-crud-page admin-delivery-zones-page">
      <div className="page-header">
        <h1>Delivery Zones</h1>
        <button className="btn-primary" onClick={openCreate}>+ New Zone</button>
      </div>
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{editing ? 'Edit Zone' : 'Create Zone'}</h2>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name *</label>
                <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={2} />
              </div>
              <div className="form-group">
                <label>Fee (ETB) *</label>
                <input type="number" value={form.fee} onChange={(e) => setForm((f) => ({ ...f, fee: e.target.value }))} min={0} step="0.01" required />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>ETA Min (days)</label>
                  <input type="number" value={form.eta_min_days} onChange={(e) => setForm((f) => ({ ...f, eta_min_days: parseInt(e.target.value, 10) || 0 }))} min={0} />
                </div>
                <div className="form-group">
                  <label>ETA Max (days)</label>
                  <input type="number" value={form.eta_max_days} onChange={(e) => setForm((f) => ({ ...f, eta_max_days: parseInt(e.target.value, 10) || 1 }))} min={1} />
                </div>
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
      ) : zones.length === 0 ? (
        <p>No delivery zones.</p>
      ) : (
        <div className="crud-list">
          {zones.map((z) => (
            <div key={z.id} className="crud-card">
              <div className="card-body">
                <h3>{z.name}</h3>
                <p className="card-meta">Fee: ETB {z.fee} · ETA: {z.eta_min_days}-{z.eta_max_days} days</p>
                <span className={`badge ${z.is_active ? 'active' : 'inactive'}`}>{z.is_active ? 'Active' : 'Inactive'}</span>
              </div>
              <div className="card-actions">
                <button className="btn-edit" onClick={() => openEdit(z)}>Edit</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
