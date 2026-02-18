import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Product } from '../../types';
import { resolveImageUrl } from '../../constants/api';
import './AdminCrudPage.css';
import './AdminProductsPage.css';

export function AdminProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');

  const load = () => {
    setLoading(true);
    adminService.listProducts({ page, search: search || undefined }).then((res) => {
      setProducts(res.data);
      setTotalPages(res.meta.total_pages);
    }).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [page]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    load();
  };

  const handleDelete = async (id: number, name: string) => {
    if (!window.confirm(`Delete product "${name}"?`)) return;
    try {
      await adminService.deleteProduct(id);
      load();
    } catch (err) {
      alert('Failed to delete product');
    }
  };

  return (
    <div className="admin-crud-page admin-products-page">
      <div className="page-header">
        <h1>Products</h1>
        <Link to="/admin/products/new" className="btn-primary">+ New Product</Link>
      </div>
      <form onSubmit={handleSearch} className="filter-bar">
        <input
          type="search"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>
      {loading ? (
        <p>Loading...</p>
      ) : products.length === 0 ? (
        <p>No products.</p>
      ) : (
        <div className="crud-grid">
          {products.map((p) => (
            <div key={p.id} className="crud-card">
              <div className="card-image">
                {p.image_url ? (
                  <img src={resolveImageUrl(p.image_url) ?? p.image_url} alt={p.name} />
                ) : (
                  <div className="placeholder">No image</div>
                )}
              </div>
              <div className="card-body">
                <h3>{p.name}</h3>
                <p className="card-meta">
                  {p.price_min && p.price_max ? `ETB ${p.price_min} - ${p.price_max}` : '—'}
                </p>
                <span className={`badge ${p.is_active ? 'active' : 'inactive'}`}>
                  {p.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="card-actions">
                <Link to={`/admin/products/${p.id}/edit`} className="btn-edit">Edit</Link>
                <Link to={`/products/${p.slug}`} className="btn-view">View</Link>
                <button type="button" className="btn-delete" onClick={() => handleDelete(p.id, p.name)}>
                  Delete
                </button>
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
