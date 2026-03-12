import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productService } from '../services/productService';
import { useCart } from '../contexts/CartContext';
import { resolveImageUrl } from '../constants/api';
import { Product, ProductVariant } from '../types';

export function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { addItem } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    if (!slug) return;
    let cancelled = false;
    setLoading(true);
    productService.getBySlug(slug).then((p) => {
      if (!cancelled) {
        setProduct(p);
        const variants = p.variants?.filter((v) => v.is_active && v.stock_qty > 0) || [];
        setSelectedVariant(variants[0] || null);
      }
      setLoading(false);
    }).catch(() => setLoading(false));
    return () => { cancelled = true; };
  }, [slug]);

  const handleAddToCart = () => {
    if (!product || !selectedVariant) return;
    addItem({
      variant_id: selectedVariant.id,
      product_id: product.id,
      product_name: product.name,
      variant_label: selectedVariant.label,
      price: String(selectedVariant.price),
      quantity,
      image_url: resolveImageUrl(product.image_url ?? product.images?.[0]?.url ?? null),
    });
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };

  if (loading || !product) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        {loading ? <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent" /> : <p className="text-black dark:text-white">Product not found.</p>}
      </div>
    );
  }

  const variants = product.variants?.filter((v) => v.is_active && v.stock_qty > 0) || [];
  const imageUrl = resolveImageUrl(product.image_url ?? product.images?.[0]?.url ?? null);

  return (
    <div className="space-y-6">
      <button type="button" onClick={() => navigate(-1)} className="rounded-lg border border-stroke dark:border-strokedark px-3 py-2 text-sm font-medium text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10">
        ← Back
      </button>
      <div className="grid gap-8 lg:grid-cols-2">
        <div className="aspect-square overflow-hidden rounded-lg border border-stroke dark:border-strokedark bg-gray-1 dark:bg-white/5">
          {imageUrl ? (
            <img src={imageUrl} alt={product.name} className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full items-center justify-center text-black dark:text-white">No image</div>
          )}
        </div>
        <div>
          <h1 className="text-2xl font-bold text-black dark:text-white">{product.name}</h1>
          {product.description && <p className="mt-2 text-black dark:text-white">{product.description}</p>}
          {variants.length > 0 ? (
            <div className="mt-6 space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-black dark:text-white">Option</label>
                <select
                  value={selectedVariant?.id || ''}
                  onChange={(e) => {
                    const v = variants.find((x) => x.id === Number(e.target.value));
                    setSelectedVariant(v || null);
                  }}
                  className="w-full rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white"
                >
                  {variants.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.label} - ETB {v.price} {v.stock_qty > 0 ? `(${v.stock_qty} in stock)` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-black dark:text-white">Quantity</label>
                <input
                  type="number"
                  min={1}
                  max={selectedVariant?.stock_qty || 1}
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value, 10) || 1))}
                  className="w-full max-w-[120px] rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 px-4 py-2.5 text-black dark:text-white"
                />
              </div>
              <button
                type="button"
                onClick={handleAddToCart}
                disabled={!selectedVariant || (selectedVariant?.stock_qty ?? 0) < quantity}
                className="w-full rounded-lg bg-primary px-4 py-3 font-medium text-white hover:opacity-90 disabled:opacity-50 sm:w-auto sm:min-w-[200px]"
              >
                {added ? 'Added to cart ✓' : 'Add to cart'}
              </button>
            </div>
          ) : (
            <p className="mt-4 text-danger">Out of stock</p>
          )}
        </div>
      </div>
    </div>
  );
}
