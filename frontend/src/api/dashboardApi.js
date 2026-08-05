import axiosClient from './axiosClient';

export const dashboardSummary = (params) =>
  axiosClient.get('/dashboard/summary/', { params });
export const dashboardWeekly = (params) =>
  axiosClient.get('/dashboard/weekly/', { params });
export const dashboardMonthly = (params) =>
  axiosClient.get('/dashboard/monthly/', { params });
export const dashboardTeam = (params) =>
  axiosClient.get('/dashboard/team-summary/', { params });
