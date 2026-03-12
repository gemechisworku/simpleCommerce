import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Product } from '../../types';
import { resolveImageUrl } from '../../constants/api';

export function AdminProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');

  const load = useCallback(() => {
    setLoading(true);
    adminService.listProducts({ page, search: search || undefined }).then((res) => {
      setProducts(res.data);
      setTotalPages(res.meta.total_pages);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [page, search]);

  useEffect(() => { load(); }, [load]);

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
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black dark:text-white">Products</h2>
          <p className="mt-1 text-body dark:text-body-dark">Manage your product catalog</p>
        </div>
        <Link
          to="/admin/products/new"
          className="inline-flex items-center justify-center rounded-lg bg-primary px-5 py-2.5 text-center font-medium text-white hover:bg-primary-dark"
        >
          + New Product
        </Link>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="search"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-stroke bg-transparent px-4 py-2.5 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white"
        />
        <button
          type="submit"
          className="rounded-lg bg-primary px-5 py-2.5 font-medium text-white hover:bg-primary-dark"
        >
          Search
        </button>
      </form>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div>
        </div>
      ) : products.length === 0 ? (
        <div className="rounded-lg border border-stroke bg-white p-12 text-center dark:border-strokedark dark:bg-meta-4">
          <p className="text-body dark:text-body-dark">No products.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((p) => (
              <div
                key={p.id}
                className="rounded-lg border border-stroke bg-white shadow-default transition hover:shadow-card-hover dark:border-strokedark dark:bg-meta-4"
              >
                <div className="aspect-[4/3] overflow-hidden rounded-t-lg bg-gray-1 dark:bg-meta-4">
                  {p.image_url ? (
                    <img
                      src={resolveImageUrl(p.image_url) ?? p.image_url}
                      alt={p.name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center text-black dark:text-white">No image</div>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-black dark:text-white">{p.name}</h3>
                  <p className="mt-1 text-sm text-body dark:text-body-dark">
                    {p.price_min && p.price_max ? `ETB ${p.price_min} - ${p.price_max}` : '—'}
                  </p>
                  <span className={`mt-2 inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${p.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}>
                    {p.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 border-t border-stroke p-4 dark:border-strokedark">
                  <Link
                    to={`/admin/products/${p.id}/edit`}
                    className="rounded-lg border border-stroke px-3 py-1.5 text-sm font-medium text-black hover:bg-gray-1 dark:border-strokedark dark:text-white dark:hover:bg-white/5"
                  >
                    Edit
                  </Link>
                  <Link
                    to={`/products/${p.slug}`}
                    className="rounded-lg border border-stroke px-3 py-1.5 text-sm font-medium text-black hover:bg-gray-1 dark:border-strokedark dark:text-white dark:hover:bg-white/5"
                  >
                    View
                  </Link>
                  <button
                    type="button"
                    onClick={() => handleDelete(p.id, p.name)}
                    className="rounded-lg border border-danger px-3 py-1.5 text-sm font-medium text-danger hover:bg-danger/10"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-body dark:text-body-dark">Page {page} of {totalPages}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((x) => Math.max(1, x - 1))}
                  disabled={page <= 1}
                  className="rounded-lg border border-stroke px-4 py-2 text-sm font-medium text-black hover:bg-gray-1 disabled:opacity-50 dark:border-strokedark dark:text-white dark:hover:bg-white/5"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((x) => Math.min(totalPages, x + 1))}
                  disabled={page >= totalPages}
                  className="rounded-lg border border-stroke px-4 py-2 text-sm font-medium text-black hover:bg-gray-1 disabled:opacity-50 dark:border-strokedark dark:text-white dark:hover:bg-white/5"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
