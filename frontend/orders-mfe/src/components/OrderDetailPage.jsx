import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchOrder, updateOrderStatus } from "../services/ordersApi";
import StatusBadge from "./StatusBadge";

const STATUS_OPTIONS = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"];

export default function OrderDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await fetchOrder(id);
      setOrder(data);
    } catch {
      setError("Order not found.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [id]);

  async function handleStatusChange(e) {
    const newStatus = e.target.value;
    setUpdatingStatus(true);
    try {
      const updated = await updateOrderStatus(id, newStatus, "operator");
      setOrder(updated);
    } catch {
      alert("Failed to update status.");
    } finally {
      setUpdatingStatus(false);
    }
  }

  if (loading) return <div className="page"><div className="loading-state"><div className="spinner" /><span>Loading…</span></div></div>;
  if (error) return <div className="page"><div className="alert alert-error">{error}</div></div>;
  if (!order) return null;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate("/orders")}>← Back to orders</button>
          <h1 className="page-title" style={{ marginTop: 8 }}>Order #{order.id.slice(0, 8)}</h1>
          <p className="page-subtitle">Created {new Date(order.created_at).toLocaleString("pt-BR")}</p>
        </div>
        <div className="status-control">
          <label htmlFor="detail-status">Status</label>
          <select
            id="detail-status"
            className="select"
            value={order.status}
            onChange={handleStatusChange}
            disabled={updatingStatus}
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="detail-grid">
        {/* Customer info */}
        <div className="card">
          <h2 className="card-title">Customer</h2>
          <dl className="detail-list">
            <div><dt>Name</dt><dd>{order.customer_name}</dd></div>
            <div><dt>Email</dt><dd>{order.customer_email}</dd></div>
          </dl>
          {order.notes && (
            <div className="notes-block">
              <dt>Notes</dt>
              <dd>{order.notes}</dd>
            </div>
          )}
        </div>

        {/* Summary */}
        <div className="card">
          <h2 className="card-title">Summary</h2>
          <dl className="detail-list">
            <div><dt>Total amount</dt><dd className="total-amount">R$ {order.total_amount.toFixed(2)}</dd></div>
            <div><dt>Items</dt><dd>{order.items.length}</dd></div>
            <div><dt>Last updated</dt><dd>{new Date(order.updated_at).toLocaleString("pt-BR")}</dd></div>
          </dl>
        </div>
      </div>

      {/* Order items */}
      <div className="card" style={{ marginTop: 20 }}>
        <h2 className="card-title">Items</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Qty</th>
              <th>Unit price</th>
              <th>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {order.items.map((item) => (
              <tr key={item.id}>
                <td className="font-medium">{item.product_name}</td>
                <td className="text-muted">{item.product_sku || "—"}</td>
                <td>{item.quantity}</td>
                <td>R$ {item.unit_price.toFixed(2)}</td>
                <td className="font-medium">R$ {(item.quantity * item.unit_price).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={4} className="font-medium" style={{ textAlign: "right" }}>Total</td>
              <td className="font-medium total-amount">R$ {order.total_amount.toFixed(2)}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      {/* Status history */}
      <div className="card" style={{ marginTop: 20 }}>
        <h2 className="card-title">Status history</h2>
        <ul className="history-list">
          {order.status_history.slice().reverse().map((entry) => (
            <li key={entry.id} className="history-item">
              <div className="history-dot" />
              <div className="history-content">
                <span className="history-transition">
                  {entry.previous_status
                    ? `${entry.previous_status} → ${entry.new_status}`
                    : `Created as ${entry.new_status}`}
                </span>
                <span className="history-meta">
                  {new Date(entry.changed_at).toLocaleString("pt-BR")}
                  {entry.changed_by ? ` · ${entry.changed_by}` : ""}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
