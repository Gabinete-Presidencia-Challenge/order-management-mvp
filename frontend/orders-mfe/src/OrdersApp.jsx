import React from "react";
import { Routes, Route } from "react-router-dom";
import OrdersListPage from "./components/OrdersListPage";
import OrderDetailPage from "./components/OrderDetailPage";
import OrderCreatePage from "./components/OrderCreatePage";
import "./styles.css";

export default function OrdersApp() {
  return (
    <Routes>
      <Route path="/orders" element={<OrdersListPage />} />
      <Route path="/orders/new" element={<OrderCreatePage />} />
      <Route path="/orders/:id" element={<OrderDetailPage />} />
    </Routes>
  );
}
