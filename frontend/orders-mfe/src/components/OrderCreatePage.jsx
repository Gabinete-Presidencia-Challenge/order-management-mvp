import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createOrder } from "../services/ordersApi";

const EMPTY_ITEM = { product_name: "", product_sku: "", quantity: 1, unit_price: "" };

export default function OrderCreatePage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    customer_name: "",
    customer_email: "",
    notes: "",
  });
  const [items, setItems] = useState([{ ...EMPTY_ITEM }]);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function updateItem(index, field, value) {
    setItems((prev) => prev.map((item, i) => i === index ? { ...item, [field]: value } : item));
  }

  function addItem() {
    setItems((prev) => [...prev, { ...EMPTY_ITEM }]);
  }

  function removeItem(index) {
    setItems((prev) => prev.filter((_, i) => i !== index));
  }

  const total = items.reduce((sum, item) => {
    const qty = parseInt(item.quantity) || 0;
    const price = parseFloat(item.unit_price) || 0;
    return sum + qty * price;
  }, 0);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    const validItems = items.filter((i) => i.product_name.trim() && i.unit_price);
    if (validItems.length === 0) {
      setError("Add at least one item with a name and price.");
      return;
    }

    const payload = {
      customer_name: form.customer_name,
      customer_email: form.customer_email,
      notes: form.notes || null,
      items: validItems.map((i) => ({
        product_name: i.product_name.trim(),
        product_sku: i.product_sku.trim() || null,
        quantity: parseInt(i.quantity),
        unit_price: parseFloat(i.unit_price),
      })),
    };

    setSubmitting(true);
    try {
      const created = await createOrder(payload);
      navigate(`/orders/${created.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create order.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate("/orders")}>← Back</button>
          <h1 className="page-title" style={{ marginTop: 8 }}>New order</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {error && <div className="alert alert-error" style={{ marginBottom: 20 }}>{error}</div>}

        {/* Customer info */}
        <div className="card">
          <h2 className="card-title">Customer information</h2>
          <div className="form-row">
            <div className="form-group">
              <label>Full name *</label>
              <input
                type="text"
                className="input"
                value={form.customer_name}
                onChange={(e) => updateField("customer_name", e.target.value)}
                placeholder="Maria Silva"
                required
              />
            </div>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                className="input"
                value={form.customer_email}
                onChange={(e) => updateField("customer_email", e.target.value)}
                placeholder="maria@example.com"
                required
              />
            </div>
          </div>
          <div className="form-group">
            <label>Notes</label>
            <textarea
              className="input textarea"
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
              placeholder="Special instructions, delivery notes…"
              rows={3}
            />
          </div>
        </div>

        {/* Order items */}
        <div className="card" style={{ marginTop: 20 }}>
          <div className="card-header-row">
            <h2 className="card-title">Items</h2>
            <button type="button" className="btn btn-ghost btn-sm" onClick={addItem}>+ Add item</button>
          </div>

          {items.map((item, index) => (
            <div key={index} className="item-row">
              <div className="form-group flex-3">
                <label>Product name *</label>
                <input
                  type="text"
                  className="input"
                  value={item.product_name}
                  onChange={(e) => updateItem(index, "product_name", e.target.value)}
                  placeholder="Widget Pro"
                  required
                />
              </div>
              <div className="form-group flex-2">
                <label>SKU</label>
                <input
                  type="text"
                  className="input"
                  value={item.product_sku}
                  onChange={(e) => updateItem(index, "product_sku", e.target.value)}
                  placeholder="SKU-001"
                />
              </div>
              <div className="form-group flex-1">
                <label>Qty *</label>
                <input
                  type="number"
                  className="input"
                  value={item.quantity}
                  onChange={(e) => updateItem(index, "quantity", e.target.value)}
                  min={1}
                  required
                />
              </div>
              <div className="form-group flex-2">
                <label>Unit price (R$) *</label>
                <input
                  type="number"
                  className="input"
                  value={item.unit_price}
                  onChange={(e) => updateItem(index, "unit_price", e.target.value)}
                  min={0}
                  step="0.01"
                  placeholder="0.00"
                  required
                />
              </div>
              {items.length > 1 && (
                <button
                  type="button"
                  className="btn btn-danger-ghost btn-sm remove-item-btn"
                  onClick={() => removeItem(index)}
                >✕</button>
              )}
            </div>
          ))}

          <div className="order-total-row">
            <span>Order total</span>
            <span className="total-amount">R$ {total.toFixed(2)}</span>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-ghost" onClick={() => navigate("/orders")}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Creating…" : "Create order"}
          </button>
        </div>
      </form>
    </div>
  );
}
