import axiosClient from './axiosClient';

export const userReport = (userId, params) =>
  axiosClient.get(`/reports/user/${userId}/`, { params });
export const weeklyReport = (params) => axiosClient.get('/reports/weekly/', { params });
export const monthlyReport = (params) =>
  axiosClient.get('/reports/monthly/', { params });
export const categoryBreakdown = (params) =>
  axiosClient.get('/reports/category-breakdown/', { params });
export const statusBreakdown = (params) =>
  axiosClient.get('/reports/status-breakdown/', { params });
export const exportCsvUrl = (params = {}) => {
  const q = new URLSearchParams(params).toString();
  const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001/api';
  return `${base}/reports/export/csv/${q ? `?${q}` : ''}`;
};
