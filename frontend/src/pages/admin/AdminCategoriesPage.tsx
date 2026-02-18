import React, { useState, useEffect } from 'react';
import { adminService, Category } from '../../services/adminService';
import './AdminCategoriesPage.css';

export function AdminCategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Category | null>(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
    parent_id: null as number | null,
    is_active: true,
    sort_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    adminService.listCategories(false).then(setCategories).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', description: '', parent_id: null, is_active: true, sort_order: 0 });
    setShowForm(true);
    setError('');
  };

  const openEdit = (c: Category) => {
    setEditing(c);
    setForm({
      name: c.name,
      description: c.description || '',
      parent_id: c.parent_id ?? null,
      is_active: c.is_active,
      sort_order: c.sort_order ?? 0,
    });
    setShowForm(true);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      if (editing) {
        await adminService.updateCategory(editing.id, {
          name: form.name,
          description: form.description || undefined,
          parent_id: form.parent_id,
          is_active: form.is_active,
          sort_order: form.sort_order,
        });
      } else {
        await adminService.createCategory({
          name: form.name,
          description: form.description || undefined,
          parent_id: form.parent_id ?? undefined,
          is_active: form.is_active,
          sort_order: form.sort_order,
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

  const handleDelete = async (c: Category) => {
    if (!window.confirm(`Delete category "${c.name}"?`)) return;
    try {
      await adminService.deleteCategory(c.id);
      load();
    } catch (err) {
      alert('Failed to delete category');
    }
  };

  return (
    <div className="admin-crud-page admin-categories-page">
      <div className="page-header">
        <h1>Categories</h1>
        <button className="btn-primary" onClick={openCreate}>+ New Category</button>
      </div>
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{editing ? 'Edit Category' : 'Create Category'}</h2>
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
                <label>Parent Category</label>
                <select
                  value={form.parent_id ?? ''}
                  onChange={(e) => setForm((f) => ({ ...f, parent_id: e.target.value ? parseInt(e.target.value, 10) : null }))}
                >
                  <option value="">None</option>
                  {categories
                    .filter((cat) => !editing || cat.id !== editing.id)
                    .map((cat) => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                </select>
              </div>
              <div className="form-group">
                <label>Sort Order</label>
                <input
                  type="number"
                  value={form.sort_order}
                  onChange={(e) => setForm((f) => ({ ...f, sort_order: parseInt(e.target.value, 10) || 0 }))}
                  min={0}
                />
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
      ) : categories.length === 0 ? (
        <p>No categories.</p>
      ) : (
        <div className="crud-list">
          {categories.map((c) => (
            <div key={c.id} className="crud-card">
              <div className="card-body">
                <h3>{c.name}</h3>
                <p className="card-meta">{c.slug} · Sort: {c.sort_order}</p>
                {c.description && <p className="card-desc">{c.description}</p>}
                <span className={`badge ${c.is_active ? 'active' : 'inactive'}`}>{c.is_active ? 'Active' : 'Inactive'}</span>
              </div>
              <div className="card-actions">
                <button className="btn-edit" onClick={() => openEdit(c)}>Edit</button>
                <button className="btn-delete" onClick={() => handleDelete(c)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
