import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { Order } from '../types';
import { ProtectedRoute } from '../components/ProtectedRoute';
import './OrderDetailPage.css';

function OrderDetailPageInner() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = Number(orderId);
    if (!id) return;
    orderService.getById(id).then(setOrder).catch(() => navigate('/orders')).finally(() => setLoading(false));
  }, [orderId, navigate]);

  const canPay = order && ['PENDING_PAYMENT', 'PAYMENT_REJECTED', 'PAYMENT_RESUBMIT_REQUESTED'].includes(order.status);
  const canCancel = order && order.status === 'PENDING_PAYMENT';

  if (loading || !order) return <div className="order-detail-page"><p>{loading ? 'Loading...' : 'Order not found.'}</p></div>;

  return (
    <div className="order-detail-page">
      <h1>Order {order.order_number}</h1>
      <p className={`status-badge status-${order.status.toLowerCase().replace(/_/g, '-')}`}>{order.status}</p>
      <div className="order-info">
        <p><strong>Total:</strong> ETB {order.total}</p>
        <p><strong>Address:</strong> {order.delivery_address}</p>
        <p><strong>Recipient:</strong> {order.recipient_name} ({order.recipient_phone})</p>
      </div>
      <div className="order-items">
        <h2>Items</h2>
        {order.items.map((i) => (
          <div key={i.id} className="order-item">
            <span>{i.product_name} {i.variant_label && `- ${i.variant_label}`}</span>
            <span>Qty: {i.quantity} x ETB {i.unit_price} = ETB {i.line_total}</span>
          </div>
        ))}
      </div>
      {order.status_history && order.status_history.length > 0 && (
        <div className="status-history">
          <h2>Status history</h2>
          {order.status_history.map((h, idx) => (
            <p key={idx}>{h.new_status} - {new Date(h.created_at).toLocaleString()}</p>
          ))}
        </div>
      )}
      <div className="order-actions">
        {canPay && <Link to={`/orders/${order.id}/payment`} className="btn-primary">Upload payment</Link>}
        {canCancel && <button className="btn-secondary" onClick={() => orderService.cancel(order.id).then(() => navigate('/orders'))}>Cancel order</button>}
      </div>
    </div>
  );
}

export function OrderDetailPage() {
  return (
    <ProtectedRoute>
      <OrderDetailPageInner />
    </ProtectedRoute>
  );
}
