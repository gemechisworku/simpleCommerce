import React, { useState, useEffect } from 'react';
import { adminService, UserListItem } from '../../services/adminService';
import './AdminCrudPage.css';
import './AdminUsersPage.css';

export function AdminUsersPage() {
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    phone: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'sales' as 'sales' | 'admin',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [roleModal, setRoleModal] = useState<{ user: UserListItem } | null>(null);
  const [newRole, setNewRole] = useState('');

  const load = () => {
    setLoading(true);
    adminService.listUsers({ page }).then((res) => {
      setUsers(res.data);
      setTotalPages(res.meta.total_pages);
    }).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [page]);

  const openCreate = () => {
    setForm({ phone: '', email: '', first_name: '', last_name: '', role: 'sales' });
    setShowForm(true);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    const phone = form.phone.startsWith('+') ? form.phone : `+251${form.phone.replace(/^0/, '')}`;
    try {
      await adminService.createUser({
        phone,
        email: form.email || undefined,
        first_name: form.first_name || undefined,
        last_name: form.last_name || undefined,
        role: form.role,
      });
      setShowForm(false);
      load();
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message
        : 'Failed to create user';
      setError(String(msg || 'Failed to create user'));
    } finally {
      setSaving(false);
    }
  };

  const openRoleModal = (user: UserListItem) => {
    setRoleModal({ user });
    setNewRole(user.role);
  };

  const handleRoleChange = async () => {
    if (!roleModal || newRole === roleModal.user.role) {
      setRoleModal(null);
      return;
    }
    try {
      await adminService.updateUserRole(roleModal.user.id, newRole);
      setRoleModal(null);
      load();
    } catch {
      alert('Failed to update role');
    }
  };

  const displayName = (u: UserListItem) => {
    if (u.first_name || u.last_name) return [u.first_name, u.last_name].filter(Boolean).join(' ');
    return u.phone || u.email || u.id.slice(0, 8);
  };

  return (
    <div className="admin-crud-page admin-users-page">
      <div className="page-header">
        <h1>Users</h1>
        <button className="btn-primary" onClick={openCreate}>+ New User</button>
      </div>
      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create Sales/Admin User</h2>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Phone *</label>
                <input value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} required placeholder="0912345678 or +251912345678" />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>First Name</label>
                  <input value={form.first_name} onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input value={form.last_name} onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))} />
                </div>
              </div>
              <div className="form-group">
                <label>Role *</label>
                <select value={form.role} onChange={(e) => setForm((f) => ({ ...f, role: e.target.value as 'sales' | 'admin' }))}>
                  <option value="sales">Sales</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Creating...' : 'Create'}</button>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
      {roleModal && (
        <div className="modal-overlay" onClick={() => setRoleModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Change Role</h2>
            <p>{displayName(roleModal.user)}</p>
            <div className="form-group">
              <label>Role</label>
              <select value={newRole} onChange={(e) => setNewRole(e.target.value)}>
                <option value="customer">Customer</option>
                <option value="sales">Sales</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="form-actions">
              <button className="btn-primary" onClick={handleRoleChange}>Update</button>
              <button className="btn-secondary" onClick={() => setRoleModal(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
      {loading ? (
        <p>Loading...</p>
      ) : users.length === 0 ? (
        <p>No users.</p>
      ) : (
        <div className="crud-list users-list">
          {users.map((u) => (
            <div key={u.id} className="crud-card">
              <div className="card-body">
                <h3>{displayName(u)}</h3>
                <p className="card-meta">{u.phone || '—'}</p>
                {u.email && <p className="card-meta">{u.email}</p>}
                <span className={`badge role-${u.role}`}>{u.role}</span>
              </div>
              <div className="card-actions">
                <button className="btn-edit" onClick={() => openRoleModal(u)}>Change Role</button>
              </div>
            </div>
          ))}
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
