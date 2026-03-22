import { useState, useEffect, useCallback } from "react";
import { fetchOrders } from "../services/ordersApi";

export function useOrders({ status, page, pageSize } = {}) {
  const [data, setData] = useState({ total: 0, items: [], page: 1, page_size: 20 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchOrders({ status, page, pageSize });
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load orders.");
    } finally {
      setLoading(false);
    }
  }, [status, page, pageSize]);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, reload: load };
}
