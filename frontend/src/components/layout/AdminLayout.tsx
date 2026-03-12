import React, { useState } from 'react';
import { Link, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { ProtectedRoute } from '../ProtectedRoute';

const navItems = [
  { path: '/admin', label: 'Dashboard', icon: '📊' },
  { path: '/admin/orders', label: 'Orders', icon: '📦' },
  { path: '/admin/payments', label: 'Payment Queue', icon: '💳' },
  { path: '/admin/products', label: 'Products', icon: '🛍️' },
  { path: '/admin/categories', label: 'Categories', icon: '📁' },
  { path: '/admin/delivery-zones', label: 'Delivery Zones', icon: '🚚' },
  { path: '/admin/payment-methods', label: 'Payment Methods', icon: '🏦' },
  { path: '/admin/users', label: 'Users', icon: '👥', adminOnly: true },
];

function AdminLayoutInner() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const handleLogout = async () => {
    setUserDropdownOpen(false);
    await logout();
    navigate('/login');
  };

  const filteredNav = navItems.filter((item) => !item.adminOnly || user?.role === 'admin');

  return (
    <div className="flex min-h-screen bg-gray-1 dark:bg-meta-4">
      {/* Sidebar backdrop (mobile) */}
      <div
        className={`fixed inset-0 z-40 bg-black/50 lg:hidden ${mobileMenuOpen ? 'block' : 'hidden'}`}
        onClick={() => setMobileMenuOpen(false)}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 flex h-full w-72 flex-col overflow-y-hidden bg-[#1C2434] transition-all duration-300 lg:translate-x-0 ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        } ${sidebarOpen ? 'lg:w-72' : 'lg:w-20'}`}
      >
        <div className="flex h-20 items-center justify-between gap-2 px-6 border-b border-white/10">
          <Link to="/admin" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-white">simpleCommerce</span>
          </Link>
          <button
            type="button"
            onClick={() => setMobileMenuOpen(false)}
            className="block lg:hidden p-2 text-white/80 hover:text-white"
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-4">
          <ul className="mb-6 flex flex-col gap-1">
            {filteredNav.map((item) => {
              const isActive = location.pathname === item.path || (item.path !== '/admin' && location.pathname.startsWith(item.path));
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 rounded-lg py-3 px-4 text-body-dark transition hover:bg-white/5 hover:text-white ${
                      isActive ? 'bg-primary text-white' : 'text-gray-400'
                    }`}
                  >
                    <span className="text-lg" aria-hidden>{item.icon}</span>
                    {sidebarOpen && <span className="font-medium">{item.label}</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
          <div className="border-t border-white/10 pt-4">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 rounded-lg py-3 px-4 text-body-dark transition hover:bg-white/5 hover:text-white"
            >
              <span className="text-lg">🏠</span>
              {sidebarOpen && <span className="font-medium">Storefront</span>}
            </Link>
          </div>
        </nav>
      </aside>

      {/* Main content area */}
      <div className={`flex flex-1 flex-col transition-all duration-300 ${sidebarOpen ? 'lg:pl-72' : 'lg:pl-20'}`}>
        {/* Header */}
        <header className="sticky top-0 z-30 flex w-full items-center justify-between gap-4 border-b border-stroke bg-white px-6 py-4 shadow-sm dark:border-strokedark dark:bg-meta-4">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className="block lg:hidden p-2 rounded-lg hover:bg-gray-2/10 text-black dark:text-white"
              aria-label="Open menu"
            >
              <span className="text-xl">☰</span>
            </button>
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden lg:flex p-2 rounded-lg hover:bg-gray-2/10 text-black dark:text-white"
              aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            >
              <span className="text-xl">{sidebarOpen ? '◀' : '▶'}</span>
            </button>
            <h1 className="text-xl font-semibold text-black dark:text-white">
              Admin
            </h1>
          </div>

          <div className="relative flex items-center gap-2 sm:gap-4">
            <button
              type="button"
              onClick={toggleTheme}
              className="p-2 rounded-lg border border-stroke bg-white dark:bg-meta-4 dark:border-strokedark text-black dark:text-white hover:opacity-80"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <span className="hidden sm:inline text-sm text-black dark:text-white">
              {user?.first_name || user?.last_name ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : user?.role}
            </span>
            <div className="relative">
              <button
                type="button"
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-2 rounded-full border border-stroke dark:border-strokedark py-2 pl-4 pr-3 text-black dark:text-white hover:border-primary hover:text-primary"
              >
                <span className="text-sm font-medium">{user?.role}</span>
                <span className="text-lg">▼</span>
              </button>
              {userDropdownOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setUserDropdownOpen(false)} aria-hidden="true" />
                  <div className="absolute right-0 top-full z-50 mt-2 w-48 rounded-lg border border-stroke dark:border-strokedark bg-white py-2 shadow-lg dark:bg-meta-4 [color-scheme:light] dark:[color-scheme:dark]">
                    <button
                      type="button"
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-gray-800 hover:bg-gray-2/10 hover:text-danger dark:text-white dark:hover:bg-white/10 dark:hover:text-danger"
                    >
                      Logout
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export function AdminLayout() {
  return (
    <ProtectedRoute roles={['sales', 'admin']}>
      <AdminLayoutInner />
    </ProtectedRoute>
  );
}
