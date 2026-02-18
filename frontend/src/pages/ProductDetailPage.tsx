import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productService } from '../services/productService';
import { useCart } from '../contexts/CartContext';
import { resolveImageUrl } from '../constants/api';
import { Product, ProductVariant } from '../types';
import './ProductDetailPage.css';

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
    return <div className="product-detail-page"><p>{loading ? 'Loading...' : 'Product not found.'}</p></div>;
  }

  const variants = product.variants?.filter((v) => v.is_active && v.stock_qty > 0) || [];
  const imageUrl = resolveImageUrl(product.image_url ?? product.images?.[0]?.url ?? null);

  return (
    <div className="product-detail-page">
      <button className="back-link" onClick={() => navigate(-1)}>← Back</button>
      <div className="product-detail-grid">
        <div className="product-image">
          {imageUrl ? (
            <img src={imageUrl} alt={product.name} />
          ) : (
            <div className="placeholder">No image</div>
          )}
        </div>
        <div className="product-details">
          <h1>{product.name}</h1>
          {product.description && <p className="description">{product.description}</p>}
          {variants.length > 0 ? (
            <>
              <div className="variant-select">
                <label>Select option:</label>
                <select
                  value={selectedVariant?.id || ''}
                  onChange={(e) => {
                    const v = variants.find((x) => x.id === Number(e.target.value));
                    setSelectedVariant(v || null);
                  }}
                >
                  {variants.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.label} - ETB {v.price} {v.stock_qty > 0 ? `(${v.stock_qty} in stock)` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div className="quantity-select">
                <label>Quantity:</label>
                <input
                  type="number"
                  min={1}
                  max={selectedVariant?.stock_qty || 1}
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value, 10) || 1))}
                />
              </div>
              <button
                className="btn-add-cart"
                onClick={handleAddToCart}
                disabled={!selectedVariant || (selectedVariant?.stock_qty ?? 0) < quantity}
              >
                {added ? 'Added to cart ✓' : 'Add to cart'}
              </button>
            </>
          ) : (
            <p className="out-of-stock">Out of stock</p>
          )}
        </div>
      </div>
    </div>
  );
}
