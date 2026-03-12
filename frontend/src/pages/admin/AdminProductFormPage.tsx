import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { adminService, Category } from '../../services/adminService';
import { Product } from '../../types';
import { resolveImageUrl } from '../../constants/api';

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

  const inputClass = "w-full rounded-lg border border-stroke bg-transparent px-4 py-2.5 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white";
  const labelClass = "mb-1.5 block text-sm font-medium text-black dark:text-white";

  if (loading) return (
    <div className="flex items-center justify-center py-16"><div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-r-transparent"></div></div>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <button type="button" onClick={() => navigate(-1)} className="rounded-lg border border-stroke px-3 py-2 text-sm font-medium hover:bg-gray-1 dark:border-strokedark dark:hover:bg-white/5">← Back</button>
        <h2 className="text-2xl font-bold text-black dark:text-white">{isEdit ? 'Edit Product' : 'Create Product'}</h2>
      </div>
      {error && <p className="rounded-lg bg-danger/10 px-4 py-2 text-sm text-danger">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <h3 className="mb-4 text-lg font-semibold text-black dark:text-white">Basic Information</h3>
          <div className="space-y-4">
            <div><label className={labelClass}>Name *</label><input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required maxLength={200} className={inputClass} /></div>
            <div><label className={labelClass}>Description</label><textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={3} className={inputClass} /></div>
            <div><label className={labelClass}>Category</label><select value={form.category_id} onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value ? Number(e.target.value) : '' }))} className={inputClass}><option value="">— None —</option>{categories.map((c) => (<option key={c.id} value={c.id}>{c.name}</option>))}</select></div>
            <div className="flex gap-6"><label className="flex items-center gap-2"><input type="checkbox" checked={form.is_featured} onChange={(e) => setForm((f) => ({ ...f, is_featured: e.target.checked }))} className="rounded border-stroke" /><span className="text-sm">Featured</span></label><label className="flex items-center gap-2"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))} className="rounded border-stroke" /><span className="text-sm">Active</span></label></div>
          </div>
        </div>
        {isEdit && (
          <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
            <h3 className="mb-4 text-lg font-semibold text-black dark:text-white">Product Images</h3>
            {images.length > 0 && (
              <div className="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
                {images.map((img) => (
                  <div key={img.id} className="relative">
                    <img src={resolveImageUrl(img.url) ?? img.url} alt={img.alt_text ?? 'Product'} className="rounded-lg border border-stroke object-cover aspect-square dark:border-strokedark" />
                    <button type="button" onClick={() => handleDeleteImage(img.id)} className="absolute right-2 top-2 rounded bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-700">Remove</button>
                  </div>
                ))}
              </div>
            )}
            <div><label className={labelClass}>Upload image (JPG/PNG, max 5MB)</label><input type="file" accept="image/jpeg,image/png,image/jpg" onChange={handleImageUpload} disabled={imageUploading} className="block w-full text-sm text-body dark:text-body-dark file:rounded file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-white" />{imageUploading && <span className="mt-1 text-sm text-body dark:text-body-dark">Uploading...</span>}</div>
          </div>
        )}
        <div className="rounded-lg border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-meta-4">
          <h3 className="mb-4 text-lg font-semibold text-black dark:text-white">Variants</h3>
          <div className="space-y-3">
            {variants.map((v, i) => (
              <div key={v.id ?? i} className="grid grid-cols-1 gap-2 sm:grid-cols-12 sm:items-center">
                <input placeholder="Label (e.g. 250g)" value={v.label} onChange={(e) => updateVariant(i, 'label', e.target.value)} required className={`rounded-lg border border-stroke bg-transparent px-3 py-2 text-black outline-none focus:border-primary dark:border-strokedark dark:text-white sm:col-span-3`} />
                <input type="number" placeholder="Price" value={v.price} onChange={(e) => updateVariant(i, 'price', e.target.value)} min={0} step="0.01" className="rounded-lg border border-stroke bg-transparent px-3 py-2 text-black dark:border-strokedark dark:text-white sm:col-span-2" />
                <input type="number" placeholder="Stock" value={v.stock_qty} onChange={(e) => updateVariant(i, 'stock_qty', parseInt(e.target.value, 10) || 0)} min={0} className="rounded-lg border border-stroke bg-transparent px-3 py-2 text-black dark:border-strokedark dark:text-white sm:col-span-2" />
                <input placeholder="SKU" value={v.sku} onChange={(e) => updateVariant(i, 'sku', e.target.value)} className="rounded-lg border border-stroke bg-transparent px-3 py-2 text-black dark:border-strokedark dark:text-white sm:col-span-2" />
                <button type="button" onClick={() => removeVariant(i)} disabled={variants.length === 1} className="rounded-lg border border-danger px-3 py-2 text-sm text-danger hover:bg-danger/10 disabled:opacity-50 sm:col-span-2">Remove</button>
              </div>
            ))}
          </div>
          <button type="button" onClick={addVariant} className="mt-4 rounded-lg border border-stroke px-4 py-2 text-sm font-medium hover:bg-gray-1 dark:border-strokedark dark:hover:bg-white/5">+ Add Variant</button>
        </div>
        <div className="flex gap-2">
          <button type="submit" disabled={saving} className="rounded-lg bg-primary px-5 py-2.5 font-medium text-white hover:bg-primary-dark disabled:opacity-50">{saving ? 'Saving...' : 'Save'}</button>
          <button type="button" onClick={() => navigate(-1)} className="rounded-lg border border-stroke px-5 py-2.5 font-medium hover:bg-gray-1 dark:border-strokedark dark:hover:bg-white/5">Cancel</button>
        </div>
      </form>
    </div>
  );
}
