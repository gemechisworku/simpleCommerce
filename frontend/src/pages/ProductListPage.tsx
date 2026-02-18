import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productService } from '../services/productService';
import { resolveImageUrl } from '../constants/api';
import { Product } from '../types';
import './ProductListPage.css';

export function ProductListPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    productService.list({ page, search: search || undefined }).then((res) => {
      if (!cancelled) {
        setProducts(res.data);
        setTotalPages(res.meta.total_pages);
      }
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, [page, search]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  return (
    <div className="product-list-page">
      <h1>Products</h1>
      <form onSubmit={handleSearch} className="search-form">
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
        <p>No products found.</p>
      ) : (
        <div className="product-grid">
          {products.map((p) => (
            <Link key={p.id} to={`/products/${p.slug}`} className="product-card">
              <div className="product-image">
                {p.image_url ? (
                  <img src={resolveImageUrl(p.image_url) ?? p.image_url} alt={p.name} />
                ) : (
                  <div className="placeholder">No image</div>
                )}
              </div>
              <div className="product-info">
                <h3>{p.name}</h3>
                <p className="price">
                  {p.price_min && p.price_max && p.price_min !== p.price_max
                    ? `ETB ${p.price_min} - ${p.price_max}`
                    : p.price_min
                    ? `ETB ${p.price_min}`
                    : '—'}
                </p>
                {!p.has_stock && <span className="out-of-stock">Out of stock</span>}
              </div>
            </Link>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>
            Previous
          </button>
          <span>Page {page} of {totalPages}</span>
          <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}
