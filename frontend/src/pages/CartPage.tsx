import React from 'react';
import { resolveImageUrl } from '../constants/api';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';

export function CartPage() {
  const { items, updateQuantity, removeItem, getCartTotal } = useCart();
  const navigate = useNavigate();

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <h1 className="text-2xl font-bold text-black dark:text-white">Your cart is empty</h1>
        <Link to="/" className="mt-4 rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:opacity-90">Continue shopping</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-black dark:text-white">Cart</h1>
      <div className="space-y-4">
        {items.map((item) => (
          <div
            key={item.variant_id}
            className="flex flex-col gap-4 rounded-lg border border-stroke dark:border-strokedark bg-white dark:bg-meta-4 p-4 sm:flex-row sm:items-center"
          >
            <div className="h-24 w-24 shrink-0 overflow-hidden rounded-lg bg-gray-1 dark:bg-white/5">
              {item.image_url ? (
                <img src={resolveImageUrl(item.image_url) ?? item.image_url} alt={item.product_name} className="h-full w-full object-cover" />
              ) : (
                <div className="flex h-full items-center justify-center text-black dark:text-white text-sm">—</div>
              )}
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="font-medium text-black dark:text-white">{item.product_name}</h3>
              <p className="text-sm text-black dark:text-white">{item.variant_label} - ETB {item.price}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => updateQuantity(item.variant_id, item.quantity - 1)}
                className="h-9 w-9 rounded-lg border border-stroke dark:border-strokedark text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10"
              >
                −
              </button>
              <span className="min-w-[2rem] text-center text-black dark:text-white">{item.quantity}</span>
              <button
                type="button"
                onClick={() => updateQuantity(item.variant_id, item.quantity + 1)}
                className="h-9 w-9 rounded-lg border border-stroke dark:border-strokedark text-black dark:text-white hover:bg-gray-1 dark:hover:bg-white/10"
              >
                +
              </button>
            </div>
            <div className="font-medium text-black dark:text-white">ETB {(parseFloat(item.price) * item.quantity).toFixed(2)}</div>
            <button
              type="button"
              onClick={() => removeItem(item.variant_id)}
              className="rounded-lg border border-danger px-3 py-1.5 text-sm text-danger hover:bg-danger/10"
            >
              Remove
            </button>
          </div>
        ))}
      </div>
      <div className="flex flex-col gap-4 border-t border-stroke dark:border-strokedark pt-6 sm:flex-row sm:items-center sm:justify-between">
        <strong className="text-lg text-black dark:text-white">Total: ETB {getCartTotal().toFixed(2)}</strong>
        <button
          type="button"
          onClick={() => navigate('/checkout')}
          className="rounded-lg bg-primary px-6 py-2.5 font-medium text-white hover:opacity-90"
        >
          Proceed to checkout
        </button>
      </div>
    </div>
  );
}
