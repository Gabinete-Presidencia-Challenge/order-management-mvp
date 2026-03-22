import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import LoginPage from "./components/LoginPage";
import "./styles.css";

const OrdersApp = React.lazy(() => import("ordersMfe/OrdersApp"));

function PrivateRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <PrivateRoute>
                <Layout>
                  <React.Suspense fallback={<div className="loading">Loading module…</div>}>
                    <Routes>
                      <Route path="/" element={<Navigate to="/orders" replace />} />
                      <Route path="/orders/*" element={<OrdersApp />} />
                    </Routes>
                  </React.Suspense>
                </Layout>
              </PrivateRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
