import React from 'react';
import { resolveImageUrl } from '../constants/api';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import './CartPage.css';

export function CartPage() {
  const { items, updateQuantity, removeItem, getCartTotal } = useCart();
  const navigate = useNavigate();

  if (items.length === 0) {
    return (
      <div className="cart-page">
        <h1>Your cart is empty</h1>
        <Link to="/" className="btn-primary">Continue shopping</Link>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <h1>Cart</h1>
      <div className="cart-items">
        {items.map((item) => (
          <div key={item.variant_id} className="cart-item">
            <div className="cart-item-image">
              {item.image_url ? <img src={resolveImageUrl(item.image_url) ?? item.image_url} alt={item.product_name} /> : <div className="placeholder">-</div>}
            </div>
            <div className="cart-item-details">
              <h3>{item.product_name}</h3>
              <p>{item.variant_label} - ETB {item.price}</p>
            </div>
            <div className="cart-item-qty">
              <button onClick={() => updateQuantity(item.variant_id, item.quantity - 1)}>-</button>
              <span>{item.quantity}</span>
              <button onClick={() => updateQuantity(item.variant_id, item.quantity + 1)}>+</button>
            </div>
            <div className="cart-item-total">ETB {(parseFloat(item.price) * item.quantity).toFixed(2)}</div>
            <button className="btn-remove" onClick={() => removeItem(item.variant_id)}>Remove</button>
          </div>
        ))}
      </div>
      <div className="cart-summary">
        <strong>Total: ETB {getCartTotal().toFixed(2)}</strong>
        <button className="btn-checkout" onClick={() => navigate('/checkout')}>Proceed to checkout</button>
      </div>
    </div>
  );
}
