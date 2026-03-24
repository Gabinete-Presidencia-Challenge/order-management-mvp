import axios from "axios";

const BASE_URL = "http://localhost:8080/api/v1";
//const BASE_URL = "http://localhost:8080/api/v1";
//const BASE_URL = process.env.ORDERS_API_URL;

function getHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchOrders({ status, page = 1, pageSize = 20 } = {}) {
  const params = { page, page_size: pageSize };
  if (status) params.status = status;
  const response = await axios.get(`${BASE_URL}/orders`, { params, headers: getHeaders() });
  return response.data;
}

export async function fetchOrder(id) {
  const response = await axios.get(`${BASE_URL}/orders/${id}`, { headers: getHeaders() });
  return response.data;
}

export async function createOrder(payload) {
  const response = await axios.post(`${BASE_URL}/orders`, payload, { headers: getHeaders() });
  return response.data;
}

export async function updateOrderStatus(id, status, changedBy) {
  const response = await axios.patch(
    `${BASE_URL}/orders/${id}/status`,
    { status, changed_by: changedBy },
    { headers: getHeaders() }
  );
  return response.data;
}

export async function deleteOrder(id) {
  await axios.delete(`${BASE_URL}/orders/${id}`, { headers: getHeaders() });
}
