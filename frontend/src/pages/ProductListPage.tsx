import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productService } from '../services/productService';
import { resolveImageUrl } from '../constants/api';
import { Product } from '../types';

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
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-black dark:text-white">Products</h1>
      <form onSubmit={handleSearch} className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <input
          type="search"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full sm:max-w-xs rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white outline-none focus:border-primary"
        />
        <button type="submit" className="rounded-lg bg-primary px-4 py-2.5 font-medium text-white hover:opacity-90">
          Search
        </button>
      </form>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent" />
        </div>
      ) : products.length === 0 ? (
        <p className="py-8 text-center text-black dark:text-white">No products found.</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {products.map((p) => (
            <Link
              key={p.id}
              to={`/products/${p.slug}`}
              className="group rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 overflow-hidden shadow-default hover:shadow-card-hover transition"
            >
              <div className="aspect-square overflow-hidden bg-gray-1 dark:bg-white/5">
                {p.image_url ? (
                  <img
                    src={resolveImageUrl(p.image_url) ?? p.image_url}
                    alt={p.name}
                    className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-black dark:text-white text-sm">No image</div>
                )}
              </div>
              <div className="p-3 sm:p-4">
                <h3 className="font-semibold text-black dark:text-white line-clamp-2">{p.name}</h3>
                <p className="mt-1 text-sm text-black dark:text-white">
                  {p.price_min && p.price_max && p.price_min !== p.price_max
                    ? `ETB ${p.price_min} - ${p.price_max}`
                    : p.price_min
                    ? `ETB ${p.price_min}`
                    : '—'}
                </p>
                {!p.has_stock && <span className="mt-1 inline-block text-xs text-danger">Out of stock</span>}
              </div>
            </Link>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex flex-wrap items-center justify-center gap-4 pt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2 text-sm font-medium text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10 disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-black dark:text-white">Page {page} of {totalPages}</span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2 text-sm font-medium text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
