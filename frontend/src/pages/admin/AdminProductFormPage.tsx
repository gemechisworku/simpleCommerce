import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { adminService, Category } from '../../services/adminService';
import { Product } from '../../types';
import './AdminProductFormPage.css';

type VariantRow = { label: string; price: string; stock_qty: number; sku: string };

export function AdminProductFormPage() {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const isEdit = !!productId;
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState<Category[]>([]);
  const [form, setForm] = useState({
    name: '',
    description: '',
    category_id: '' as number | '',
    is_active: true,
    is_featured: false,
  });
  const [variants, setVariants] = useState<VariantRow[]>([{ label: '', price: '', stock_qty: 0, sku: '' }]);

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
          label: v.label,
          price: String(v.price),
          stock_qty: v.stock_qty,
          sku: v.sku || '',
        })));
      }
    }).catch(() => setError('Failed to load product')).finally(() => setLoading(false));
  }, [productId]);

  const addVariant = () => {
    setVariants((v) => [...v, { label: '', price: '', stock_qty: 0, sku: '' }]);
  };

  const removeVariant = (i: number) => {
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
      if (isEdit) {
        await adminService.updateProduct(Number(productId), {
          name: form.name,
          description: form.description || undefined,
          category_id: form.category_id || undefined,
          is_active: form.is_active,
          is_featured: form.is_featured,
        });
        // Add only new variants (existing variants shown read-only; full variant edit could be added later)
        const existingCount = (await adminService.getProduct(Number(productId))).variants?.length ?? 0;
        const newVariants = variantPayload.slice(existingCount);
        for (const v of newVariants) {
          await adminService.createVariant(Number(productId), v);
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
        <div className="form-section">
          <h2>Variants</h2>
          {variants.map((v, i) => (
            <div key={i} className="variant-row">
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
