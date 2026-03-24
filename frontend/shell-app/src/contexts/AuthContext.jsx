import React, { createContext, useContext, useState, useCallback } from "react";
import axios from "axios";

const AuthContext = createContext(null);

//const USERS_API = "http://localhost:8080/api/users/v1";
const USERS_API = process.env.USERS_API_URL;



export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  const login = useCallback(async (email, password) => {
    try {
      const response = await axios.post(`${USERS_API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      return userData;
    } catch (err) {
      // Surface the exact backend error message when available
      const detail = err.response?.data?.detail;
      const status = err.response?.status;
      if (status === 401) throw new Error("Invalid email or password.");
      if (status === 403) throw new Error("Account is inactive. Contact your administrator.");
      if (status === 422) throw new Error("Invalid request. Check email format.");
      if (detail)         throw new Error(detail);
      if (!err.response)  throw new Error(`Cannot reach the server. Is it running on ${USERS_API}?`);
      throw new Error("Login failed. Please try again.");
    } 
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
