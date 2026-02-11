/**
 * Industrial Wearable AI — API Client
 * Axios instance with baseURL and Authorization header.
 */
import axios from "axios";
import { toast } from "react-hot-toast";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err?.response?.status;
    const detail = err?.response?.data?.detail;
    let msg = "Request failed";
    if (typeof detail === "string") msg = detail;
    else if (Array.isArray(detail) && detail[0]?.msg) msg = detail[0].msg;
    else if (detail?.msg) msg = detail.msg;

    if (status === 401) {
      const url = err?.config?.url ?? "";
      const isAuthEndpoint = /\/api\/auth\/(login|register)$/.test(url);
      if (!isAuthEndpoint) {
        localStorage.removeItem("access_token");
        toast.error("Session expired. Please log in again.");
        window.location.href = "/login";
      }
    } else if (status && status >= 400) {
      toast.error(msg);
    }
    return Promise.reject(err);
  }
);
