import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useOrders } from "../hooks/useOrders";
import { updateOrderStatus, deleteOrder } from "../services/ordersApi";
import StatusBadge from "./StatusBadge";

const STATUS_OPTIONS = ["", "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"];

export default function OrdersListPage() {
  const navigate = useNavigate();
  const [selectedStatus, setSelectedStatus] = useState("");
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 15;

  const { data, loading, error, reload } = useOrders({
    status: selectedStatus || undefined,
    page,
    pageSize: PAGE_SIZE,
  });

  const totalPages = Math.ceil(data.total / PAGE_SIZE);

  function handleStatusChange(e) {
    setSelectedStatus(e.target.value);
    setPage(1);
  }

  async function handleQuickStatus(orderId, newStatus) {
    try {
      await updateOrderStatus(orderId, newStatus, "operator");
      reload();
    } catch {
      alert("Failed to update status.");
    }
  }

  async function handleDelete(orderId) {
    if (!confirm("Delete this order? This cannot be undone.")) return;
    try {
      await deleteOrder(orderId);
      reload();
    } catch {
      alert("Failed to delete order.");
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Orders</h1>
          <p className="page-subtitle">{data.total} order{data.total !== 1 ? "s" : ""} total</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate("/orders/new")}>
          + New order
        </button>
      </div>

      <div className="toolbar">
        <div className="filter-group">
          <label htmlFor="status-filter">Filter by status</label>
          <select id="status-filter" value={selectedStatus} onChange={handleStatusChange} className="select">
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s === "" ? "All statuses" : s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </div>
        <button className="btn btn-ghost" onClick={reload}>↻ Refresh</button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading-state">
          <div className="spinner" />
          <span>Loading orders…</span>
        </div>
      ) : data.items.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">🗂</span>
          <p>No orders found.</p>
          <button className="btn btn-primary" onClick={() => navigate("/orders/new")}>Create your first order</button>
        </div>
      ) : (
        <>
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Total</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((order) => (
                  <tr key={order.id} className="table-row" onClick={() => navigate(`/orders/${order.id}`)}>
                    <td className="order-id">{order.id.slice(0, 8)}…</td>
                    <td className="font-medium">{order.customer_name}</td>
                    <td className="text-muted">{order.customer_email}</td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <select
                        className="status-select"
                        value={order.status}
                        onChange={(e) => handleQuickStatus(order.id, e.target.value)}
                      >
                        {STATUS_OPTIONS.filter(Boolean).map((s) => (
                          <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                        ))}
                      </select>
                    </td>
                    <td className="font-medium">R$ {order.total_amount.toFixed(2)}</td>
                    <td className="text-muted">{new Date(order.created_at).toLocaleDateString("pt-BR")}</td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <button
                        className="btn btn-danger-ghost btn-sm"
                        onClick={() => handleDelete(order.id)}
                        title="Delete order"
                      >✕</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button className="btn btn-ghost btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>
                ← Prev
              </button>
              <span className="pagination-info">Page {page} of {totalPages}</span>
              <button className="btn btn-ghost btn-sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
