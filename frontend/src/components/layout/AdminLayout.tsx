import React, { useState } from 'react';
import { Link, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ProtectedRoute } from '../ProtectedRoute';
import './Layout.css';

function AdminLayoutInner() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="layout admin-layout">
      <header className="layout-header">
        <div className="header-content">
          <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Menu">☰</button>
          <Link to="/admin" className="logo">simpleCommerce Admin</Link>
          <nav className="nav-desktop">
            <Link to="/admin">Dashboard</Link>
            <Link to="/admin/orders">Orders</Link>
            <Link to="/admin/payments">Payments</Link>
            <Link to="/admin/products">Products</Link>
            <Link to="/admin/categories">Categories</Link>
            <Link to="/admin/delivery-zones">Delivery Zones</Link>
            <Link to="/admin/payment-methods">Payment Methods</Link>
            {user?.role === 'admin' && <Link to="/admin/users">Users</Link>}
            <Link to="/">Store</Link>
          </nav>
          <div className="header-actions">
            <span className="user-name">{user?.first_name || user?.role}</span>
            <button className="btn-logout" onClick={handleLogout}>Logout</button>
          </div>
        </div>
        {menuOpen && (
          <nav className="nav-mobile open">
            <Link to="/admin" onClick={() => setMenuOpen(false)}>Dashboard</Link>
            <Link to="/admin/orders" onClick={() => setMenuOpen(false)}>Orders</Link>
            <Link to="/admin/payments" onClick={() => setMenuOpen(false)}>Payments</Link>
            <Link to="/admin/products" onClick={() => setMenuOpen(false)}>Products</Link>
            <Link to="/admin/categories" onClick={() => setMenuOpen(false)}>Categories</Link>
            <Link to="/admin/delivery-zones" onClick={() => setMenuOpen(false)}>Delivery Zones</Link>
            <Link to="/admin/payment-methods" onClick={() => setMenuOpen(false)}>Payment Methods</Link>
            {user?.role === 'admin' && <Link to="/admin/users" onClick={() => setMenuOpen(false)}>Users</Link>}
            <Link to="/" onClick={() => setMenuOpen(false)}>Store</Link>
          </nav>
        )}
      </header>
      <main className="layout-main"><Outlet /></main>
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
