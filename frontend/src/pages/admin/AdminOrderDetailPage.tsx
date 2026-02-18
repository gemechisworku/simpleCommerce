import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminService } from '../../services/adminService';
import { Order } from '../../types';
import './AdminOrderDetailPage.css';

export function AdminOrderDetailPage() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = Number(orderId);
    if (!id) return;
    adminService.getOrder(id).then(setOrder).catch(() => navigate('/admin/orders')).finally(() => setLoading(false));
  }, [orderId, navigate]);

  if (loading || !order) return <p>{loading ? 'Loading...' : 'Order not found.'}</p>;

  return (
    <div className="admin-order-detail">
      <button className="back-link" onClick={() => navigate(-1)}>Back</button>
      <h1>Order {order.order_number}</h1>
      <p className="status-badge">{order.status}</p>
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
    </div>
  );
}
