import React from "react";

const STATUS_STYLES = {
  pending:    { bg: "#fff8e1", color: "#f57f17", label: "Pending" },
  confirmed:  { bg: "#e3f2fd", color: "#1565c0", label: "Confirmed" },
  processing: { bg: "#ede7f6", color: "#4527a0", label: "Processing" },
  shipped:    { bg: "#e8f5e9", color: "#2e7d32", label: "Shipped" },
  delivered:  { bg: "#e0f2f1", color: "#00695c", label: "Delivered" },
  cancelled:  { bg: "#fce4ec", color: "#b71c1c", label: "Cancelled" },
};

export default function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || { bg: "#f5f5f5", color: "#616161", label: status };
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 10px",
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 500,
        background: style.bg,
        color: style.color,
        whiteSpace: "nowrap",
      }}
    >
      {style.label}
    </span>
  );
}
