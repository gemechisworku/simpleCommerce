import React, { useState } from 'react';
import { Link, useNavigate, Outlet } from 'react-router-dom';
import { useAuth, useCart } from '../../contexts';
import { useTheme } from '../../contexts/ThemeContext';

export function StorefrontLayout() {
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { itemCount } = useCart();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-meta-4 text-black dark:text-white">
      <header className="sticky top-0 z-40 border-b border-stroke dark:border-strokedark bg-white dark:bg-meta-4 shadow-sm">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-2 rounded-lg lg:hidden text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10"
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <Link to="/" className="text-lg font-bold text-primary hover:opacity-90">
            simpleCommerce
          </Link>
          <nav className={`absolute left-0 right-0 top-14 z-50 flex flex-col gap-1 border-b border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-4 lg:static lg:flex-row lg:border-0 lg:p-0 ${menuOpen ? 'flex' : 'hidden lg:flex'}`}>
            <Link to="/" onClick={() => setMenuOpen(false)} className="rounded-lg px-4 py-2 text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10 lg:px-3">
              Products
            </Link>
            {isAuthenticated && <Link to="/orders" onClick={() => setMenuOpen(false)} className="rounded-lg px-4 py-2 text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10 lg:px-3">My Orders</Link>}
            {isAuthenticated && (user?.role === 'admin' || user?.role === 'sales') && (
              <Link to="/admin" onClick={() => setMenuOpen(false)} className="rounded-lg px-4 py-2 text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10 lg:px-3">Admin</Link>
            )}
          </nav>
          <div className="flex items-center gap-2 sm:gap-4">
            <button
              type="button"
              onClick={toggleTheme}
              className="p-2 rounded-lg border border-stroke dark:border-strokedark text-black dark:text-white hover:opacity-80"
              aria-label={theme === 'dark' ? 'Light mode' : 'Dark mode'}
              title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <Link to="/cart" className="relative p-2 rounded-lg text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10">
              🛒
              {itemCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs font-medium text-white">
                  {itemCount > 99 ? '99+' : itemCount}
                </span>
              )}
            </Link>
            {isAuthenticated ? (
              <div className="flex items-center gap-2">
                <span className="hidden sm:inline text-sm text-black dark:text-white">
                  {user?.first_name || user?.phone || 'Account'}
                </span>
                <button onClick={handleLogout} className="rounded-lg border border-stroke dark:border-strokedark px-3 py-1.5 text-sm text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10">
                  Logout
                </button>
              </div>
            ) : (
              <Link to="/login" className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:opacity-90">
                Login
              </Link>
            )}
          </div>
        </div>
        {menuOpen && <div className="fixed inset-0 z-40 bg-black/30 lg:hidden" onClick={() => setMenuOpen(false)} aria-hidden="true" />}
      </header>
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <Outlet />
      </main>
      <footer className="border-t border-stroke dark:border-strokedark bg-white dark:bg-meta-4 py-6 text-center text-sm text-black dark:text-white">
        <div className="mx-auto max-w-6xl px-4 flex flex-wrap items-center justify-center gap-4">
          <Link to="/" className="hover:underline">About</Link>
          <Link to="/" className="hover:underline">Contact</Link>
          <span>© {new Date().getFullYear()} simpleCommerce</span>
        </div>
      </footer>
    </div>
  );
}
