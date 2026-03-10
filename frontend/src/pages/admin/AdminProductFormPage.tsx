import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { adminService, Category } from '../../services/adminService';
import { Product } from '../../types';
import { resolveImageUrl } from '../../constants/api';
import './AdminProductFormPage.css';

type VariantRow = { id?: number; label: string; price: string; stock_qty: number; sku: string };

type ProductImageItem = { id: number; url: string; alt_text?: string | null; sort_order: number };

export function AdminProductFormPage() {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const isEdit = !!productId;
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState<Category[]>([]);
  const [images, setImages] = useState<ProductImageItem[]>([]);
  const [imageUploading, setImageUploading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    description: '',
    category_id: '' as number | '',
    is_active: true,
    is_featured: false,
  });
  const [variants, setVariants] = useState<VariantRow[]>([{ label: '', price: '', stock_qty: 0, sku: '' }]);
  const [variantIdsToDelete, setVariantIdsToDelete] = useState<number[]>([]);

  useEffect(() => {
    adminService.listCategories(false).then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    if (!productId) return;
    adminService.getProduct(Number(productId)).then((p: Product) => {
      setForm({
        name: p.name,
        description: p.description || '',
        category_id: p.category_id ?? '',
        is_active: p.is_active ?? true,
        is_featured: p.is_featured ?? false,
      });
      if (p.variants && p.variants.length > 0) {
        setVariants(p.variants.map((v) => ({
          id: v.id,
          label: v.label,
          price: String(v.price),
          stock_qty: v.stock_qty,
          sku: v.sku || '',
        })));
      }
      setVariantIdsToDelete([]);
    }).catch(() => setError('Failed to load product')).finally(() => setLoading(false));
  }, [productId]);

  const loadImages = () => {
    if (!productId) return;
    adminService.listProductImages(Number(productId)).then(setImages).catch(() => {});
  };

  useEffect(() => {
    if (isEdit && productId) loadImages();
  }, [isEdit, productId]);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !productId) return;
    setImageUploading(true);
    try {
      await adminService.uploadProductImage(Number(productId), file);
      loadImages();
    } catch {
      setError('Failed to upload image');
    } finally {
      setImageUploading(false);
      e.target.value = '';
    }
  };

  const handleDeleteImage = async (imageId: number) => {
    if (!productId || !window.confirm('Delete this image?')) return;
    try {
      await adminService.deleteProductImage(Number(productId), imageId);
      loadImages();
    } catch {
      setError('Failed to delete image');
    }
  };

  const addVariant = () => {
    setVariants((v) => [...v, { label: '', price: '', stock_qty: 0, sku: '' }]);
  };

  const removeVariant = (i: number) => {
    const row = variants[i];
    if (row?.id) setVariantIdsToDelete((ids) => [...ids, row.id!]);
    setVariants((v) => v.filter((_, j) => j !== i));
  };

  const updateVariant = (i: number, field: keyof VariantRow, value: string | number) => {
    setVariants((v) => v.map((row, j) => (j === i ? { ...row, [field]: value } : row)));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    const variantPayload = variants
      .filter((v) => v.label.trim())
      .map((v) => ({
        label: v.label.trim(),
        price: v.price || '0',
        stock_qty: Number(v.stock_qty) || 0,
        sku: v.sku || undefined,
      }));
    if (variantPayload.length === 0) {
      setError('At least one variant is required');
      setSaving(false);
      return;
    }
    try {
      if (isEdit && productId) {
        await adminService.updateProduct(Number(productId), {
          name: form.name,
          description: form.description || undefined,
          category_id: form.category_id || undefined,
          is_active: form.is_active,
          is_featured: form.is_featured,
        });
        for (const id of variantIdsToDelete) {
          await adminService.deleteVariant(id);
        }
        for (const row of variants) {
          const payload = {
            label: row.label.trim(),
            price: row.price || '0',
            stock_qty: Number(row.stock_qty) || 0,
            sku: row.sku || undefined,
          };
          if (row.id) {
            await adminService.updateVariant(row.id, payload);
          } else if (row.label.trim()) {
            await adminService.createVariant(Number(productId), {
              ...payload,
              is_active: true,
            });
          }
        }
      } else {
        await adminService.createProduct({
          name: form.name,
          description: form.description || undefined,
          category_id: form.category_id || undefined,
          is_active: form.is_active,
          is_featured: form.is_featured,
          variants: variantPayload,
        });
      }
      navigate('/admin/products');
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message
        : 'Failed to save';
      setError(String(msg || 'Failed to save'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="admin-form-page"><p>Loading...</p></div>;

  return (
    <div className="admin-form-page admin-product-form">
      <button className="back-link" onClick={() => navigate(-1)}>← Back</button>
      <h1>{isEdit ? 'Edit Product' : 'Create Product'}</h1>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h2>Basic Information</h2>
          <div className="form-group">
            <label>Name *</label>
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              required
              maxLength={200}
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={3}
            />
          </div>
          <div className="form-group">
            <label>Category</label>
            <select
              value={form.category_id}
              onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value ? Number(e.target.value) : '' }))}
            >
              <option value="">— None —</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <label><input type="checkbox" checked={form.is_featured} onChange={(e) => setForm((f) => ({ ...f, is_featured: e.target.checked }))} /> Featured</label>
            <label><input type="checkbox" checked={form.is_active} onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))} /> Active</label>
          </div>
        </div>
        {isEdit && (
          <div className="form-section">
            <h2>Product Images</h2>
            {images.length > 0 && (
              <div className="product-images-grid">
                {images.map((img) => (
                  <div key={img.id} className="product-image-item">
                    <img src={resolveImageUrl(img.url) ?? img.url} alt={img.alt_text ?? 'Product'} />
                    <button type="button" className="btn-remove" onClick={() => handleDeleteImage(img.id)}>Remove</button>
                  </div>
                ))}
              </div>
            )}
            <div className="form-group">
              <label>Upload image (JPG/PNG, max 5MB)</label>
              <input type="file" accept="image/jpeg,image/png,image/jpg" onChange={handleImageUpload} disabled={imageUploading} />
              {imageUploading && <span className="muted">Uploading...</span>}
            </div>
          </div>
        )}
        <div className="form-section">
          <h2>Variants</h2>
          {variants.map((v, i) => (
            <div key={v.id ?? i} className="variant-row">
              <input placeholder="Label (e.g. 250g)" value={v.label} onChange={(e) => updateVariant(i, 'label', e.target.value)} required />
              <input type="number" placeholder="Price" value={v.price} onChange={(e) => updateVariant(i, 'price', e.target.value)} min={0} step="0.01" />
              <input type="number" placeholder="Stock" value={v.stock_qty} onChange={(e) => updateVariant(i, 'stock_qty', parseInt(e.target.value, 10) || 0)} min={0} />
              <input placeholder="SKU" value={v.sku} onChange={(e) => updateVariant(i, 'sku', e.target.value)} />
              <button type="button" className="btn-remove" onClick={() => removeVariant(i)} disabled={variants.length === 1}>Remove</button>
            </div>
          ))}
          <button type="button" className="btn-secondary" onClick={addVariant}>+ Add Variant</button>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
          <button type="button" className="btn-secondary" onClick={() => navigate(-1)}>Cancel</button>
        </div>
      </form>
    </div>
  );
}
