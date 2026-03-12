import React, { useState, useEffect } from 'react';
import { adminService, Category } from '../../services/adminService';

const inputClass = "w-full rounded-lg border border-stroke bg-transparent px-4 py-2.5 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white";
const labelClass = "mb-1.5 block text-sm font-medium text-black dark:text-white";
const btnPrimary = "rounded-lg bg-primary px-4 py-2 font-medium text-white hover:bg-primary-dark disabled:opacity-50";
const btnSecondary = "rounded-lg border border-stroke px-4 py-2 font-medium text-black hover:bg-gray-1 dark:border-strokedark dark:text-white dark:hover:bg-white/5";

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
        await adminService.updateCategory(editing.id, { name: form.name, description: form.description || undefined, parent_id: form.parent_id, is_active: form.is_active, sort_order: form.sort_order });
      } else {
        await adminService.createCategory({ name: form.name, description: form.description || undefined, parent_id: form.parent_id ?? undefined, is_active: form.is_active, sort_order: form.sort_order });
      }
      setShowForm(false);
      load();
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message : 'Failed to save';
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
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black dark:text-white">Categories</h2>
          <p className="mt-1 text-body dark:text-body-dark">Organize products by category</p>
        </div>
        <button type="button" onClick={openCreate} className={btnPrimary}>+ New Category</button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setShowForm(false)}>
          <div className="w-full max-w-md rounded-lg border border-stroke bg-white p-6 shadow-xl dark:border-strokedark dark:bg-meta-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-black dark:text-white">{editing ? 'Edit Category' : 'Create Category'}</h3>
            {error && <p className="mt-2 text-sm text-danger">{error}</p>}
            <form onSubmit={handleSubmit} className="mt-4 space-y-4">
              <div><label className={labelClass}>Name *</label><input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required className={inputClass} /></div>
              <div><label className={labelClass}>Description</label><textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={2} className={inputClass} /></div>
              <div>
                <label className={labelClass}>Parent Category</label>
                <select value={form.parent_id ?? ''} onChange={(e) => setForm((f) => ({ ...f, parent_id: e.target.value ? parseInt(e.target.value, 10) : null }))} className={inputClass}>
                  <option value="">None</option>
                  {categories.filter((cat) => !editing || cat.id !== editing.id).map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div><label className={labelClass}>Sort Order</label><input type="number" value={form.sort_order} onChange={(e) => setForm((f) => ({ ...f, sort_order: parseInt(e.target.value, 10) || 0 }))} min={0} className={inputClass} /></div>
              <label className="flex items-center gap-2"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))} className="rounded border-stroke" /><span className="text-sm text-black dark:text-white">Active</span></label>
              <div className="flex gap-2 pt-2"><button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button><button type="button" className={btnSecondary} onClick={() => setShowForm(false)}>Cancel</button></div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16"><div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div></div>
      ) : categories.length === 0 ? (
        <div className="rounded-lg border border-stroke bg-white p-12 text-center dark:border-strokedark dark:bg-meta-4"><p className="text-body dark:text-body-dark">No categories.</p></div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((c) => (
            <div key={c.id} className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
              <h3 className="font-semibold text-black dark:text-white">{c.name}</h3>
              <p className="mt-1 text-sm text-body dark:text-body-dark">{c.slug} · Sort: {c.sort_order}</p>
              {c.description && <p className="mt-1 text-sm text-body dark:text-body-dark">{c.description}</p>}
              <span className={`mt-2 inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${c.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}>{c.is_active ? 'Active' : 'Inactive'}</span>
              <div className="mt-4 flex gap-2">
                <button type="button" onClick={() => openEdit(c)} className={btnSecondary}>Edit</button>
                <button type="button" onClick={() => handleDelete(c)} className="rounded-lg border border-danger px-3 py-1.5 text-sm font-medium text-danger hover:bg-danger/10">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
