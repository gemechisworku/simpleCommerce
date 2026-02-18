import React, { useState } from 'react';
import { Link, useNavigate, Outlet } from 'react-router-dom';
import { useAuth, useCart } from '../../contexts';
import './Layout.css';

export function StorefrontLayout() {
  const { user, isAuthenticated, logout } = useAuth();
  const { itemCount } = useCart();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="layout storefront-layout">
      <header className="layout-header">
        <div className="header-content">
          <button
            className="menu-toggle"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <Link to="/" className="logo">
            simpleCommerce
          </Link>
          <nav className={`nav-desktop ${menuOpen ? 'open' : ''}`}>
            <Link to="/" onClick={() => setMenuOpen(false)}>Products</Link>
            {isAuthenticated && <Link to="/orders" onClick={() => setMenuOpen(false)}>My Orders</Link>}
            {isAuthenticated && (user?.role === 'admin' || user?.role === 'sales') && (
              <Link to="/admin" onClick={() => setMenuOpen(false)}>Admin</Link>
            )}
          </nav>
          <div className="header-actions">
            <Link to="/cart" className="cart-link">
              🛒
              {itemCount > 0 && <span className="badge">{itemCount}</span>}
            </Link>
            {isAuthenticated ? (
              <div className="user-menu">
                <span className="user-name">
                  {user?.first_name || user?.phone || 'Account'}
                </span>
                <button onClick={handleLogout} className="btn-logout">
                  Logout
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn-login">
                Login
              </Link>
            )}
          </div>
        </div>
        {menuOpen && (
          <nav className="nav-mobile open">
            <Link to="/" onClick={() => setMenuOpen(false)}>Products</Link>
            {isAuthenticated && <Link to="/orders" onClick={() => setMenuOpen(false)}>My Orders</Link>}
            <Link to="/cart" onClick={() => setMenuOpen(false)}>Cart ({itemCount})</Link>
            {isAuthenticated && (user?.role === 'admin' || user?.role === 'sales') && (
              <Link to="/admin" onClick={() => setMenuOpen(false)}>Admin</Link>
            )}
            {isAuthenticated ? (
              <button onClick={() => { handleLogout(); setMenuOpen(false); }}>Logout</button>
            ) : (
              <Link to="/login" onClick={() => setMenuOpen(false)}>Login</Link>
            )}
          </nav>
        )}
      </header>
      <main className="layout-main"><Outlet /></main>
      <footer className="layout-footer">
        <div className="footer-content">
          <Link to="/">About</Link>
          <Link to="/">Contact</Link>
          <span>© {new Date().getFullYear()} simpleCommerce</span>
        </div>
      </footer>
    </div>
  );
}
