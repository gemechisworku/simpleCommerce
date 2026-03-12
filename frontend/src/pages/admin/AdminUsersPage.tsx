import React, { useState, useEffect, useCallback } from 'react';
import { adminService, UserListItem } from '../../services/adminService';

const inputClass = "w-full rounded-lg border border-stroke bg-transparent px-4 py-2.5 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white";
const labelClass = "mb-1.5 block text-sm font-medium text-black dark:text-white";
const btnPrimary = "rounded-lg bg-primary px-4 py-2 font-medium text-white hover:bg-primary-dark disabled:opacity-50";
const btnSecondary = "rounded-lg border border-stroke px-4 py-2 font-medium text-black hover:bg-gray-1 dark:border-strokedark dark:text-white dark:hover:bg-white/5";

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

  const load = useCallback(() => {
    setLoading(true);
    adminService.listUsers({ page }).then((res) => {
      setUsers(res.data);
      setTotalPages(res.meta.total_pages);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [page]);

  useEffect(() => { load(); }, [load]);

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

  const roleBadge = (role: string) => {
    const map: Record<string, string> = { admin: 'bg-violet-100 text-violet-800', sales: 'bg-blue-100 text-blue-800', customer: 'bg-gray-100 text-gray-800' };
    return map[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black dark:text-white">Users</h2>
          <p className="mt-1 text-body dark:text-body-dark">Create and manage sales/admin users</p>
        </div>
        <button type="button" onClick={openCreate} className={btnPrimary}>+ New User</button>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setShowForm(false)}>
          <div className="w-full max-w-md rounded-lg border border-stroke bg-white p-6 shadow-xl dark:border-strokedark dark:bg-meta-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-black dark:text-white">Create Sales/Admin User</h3>
            {error && <p className="mt-2 text-sm text-danger">{error}</p>}
            <form onSubmit={handleSubmit} className="mt-4 space-y-4">
              <div><label className={labelClass}>Phone *</label><input value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} required placeholder="0912345678 or +251912345678" className={inputClass} /></div>
              <div><label className={labelClass}>Email</label><input type="email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} className={inputClass} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className={labelClass}>First Name</label><input value={form.first_name} onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))} className={inputClass} /></div>
                <div><label className={labelClass}>Last Name</label><input value={form.last_name} onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))} className={inputClass} /></div>
              </div>
              <div><label className={labelClass}>Role *</label><select value={form.role} onChange={(e) => setForm((f) => ({ ...f, role: e.target.value as 'sales' | 'admin' }))} className={inputClass}><option value="sales">Sales</option><option value="admin">Admin</option></select></div>
              <div className="flex gap-2 pt-2"><button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Creating...' : 'Create'}</button><button type="button" className={btnSecondary} onClick={() => setShowForm(false)}>Cancel</button></div>
            </form>
          </div>
        </div>
      )}

      {roleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setRoleModal(null)}>
          <div className="w-full max-w-sm rounded-lg border border-stroke bg-white p-6 shadow-xl dark:border-strokedark dark:bg-meta-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-black dark:text-white">Change Role</h3>
            <p className="mt-2 text-body">{displayName(roleModal.user)}</p>
            <div className="mt-4"><label className={labelClass}>Role</label><select value={newRole} onChange={(e) => setNewRole(e.target.value)} className={inputClass}><option value="customer">Customer</option><option value="sales">Sales</option><option value="admin">Admin</option></select></div>
            <div className="mt-6 flex gap-2"><button type="button" onClick={handleRoleChange} className={btnPrimary}>Update</button><button type="button" className={btnSecondary} onClick={() => setRoleModal(null)}>Cancel</button></div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16"><div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div></div>
      ) : users.length === 0 ? (
        <div className="rounded-lg border border-stroke bg-white p-12 text-center dark:border-strokedark dark:bg-meta-4"><p className="text-body dark:text-body-dark">No users.</p></div>
      ) : (
        <div className="rounded-lg border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-meta-4">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead><tr className="border-b border-stroke text-left dark:border-strokedark"><th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Name</th><th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Contact</th><th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Role</th><th className="px-6 py-4 text-sm font-medium text-black dark:text-white">Action</th></tr></thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-stroke hover:bg-gray-1/50 dark:border-strokedark dark:hover:bg-white/5">
                    <td className="px-6 py-4 font-medium text-black dark:text-white">{displayName(u)}</td>
                    <td className="px-6 py-4 text-body dark:text-body-dark">{u.phone || '—'}{u.email && ` · ${u.email}`}</td>
                    <td className="px-6 py-4"><span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${roleBadge(u.role)}`}>{u.role}</span></td>
                    <td className="px-6 py-4"><button type="button" onClick={() => openRoleModal(u)} className="text-primary font-medium hover:underline">Change Role</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-stroke px-6 py-4 dark:border-strokedark">
              <p className="text-sm text-body dark:text-body-dark">Page {page} of {totalPages}</p>
              <div className="flex gap-2">
                <button onClick={() => setPage((x) => Math.max(1, x - 1))} disabled={page <= 1} className={btnSecondary}>Previous</button>
                <button onClick={() => setPage((x) => Math.min(totalPages, x + 1))} disabled={page >= totalPages} className={btnSecondary}>Next</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
