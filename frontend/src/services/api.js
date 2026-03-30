import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

export const api = axios.create({
  baseURL: API_BASE
});

export const predictXray = async (formData) => {
  const { data } = await api.post("/predict-xray", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
};

export const predictEye = async (formData) => {
  const { data } = await api.post("/predict-eye", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
};

export const fetchHistory = async () => {
  const { data } = await api.get("/history");
  return data;
};

export const downloadReport = async (id) => {
  const response = await api.get(`/download-report?id=${id}`, { responseType: "blob" });
  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `report_${id}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const downloadReportUrl = (id) => `${API_BASE}/download-report?id=${id}`;
export const fileUrl = (path) => `${API_BASE}${path}`;
