import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-icon">📦</span>
          <span className="brand-name">OrderOps</span>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/orders" className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            <span>🗂</span> Orders
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-name">{user?.full_name}</span>
            <span className="user-role">{user?.role}</span>
          </div>
          <button className="btn-logout" onClick={logout}>Sign out</button>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
