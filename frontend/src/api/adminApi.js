import axiosClient from './axiosClient';

export const listUsers = (params) => axiosClient.get('/users/', { params });
export const getUser = (id) => axiosClient.get(`/users/${id}/`);
export const createUser = (payload) => axiosClient.post('/users/', payload);
export const updateUser = (id, payload) => axiosClient.patch(`/users/${id}/`, payload);
export const myTeam = () => axiosClient.get('/users/my-team/');

export const listDepartments = (params) =>
  axiosClient.get('/departments/', { params });
export const createDepartment = (payload) =>
  axiosClient.post('/departments/', payload);
export const updateDepartment = (id, payload) =>
  axiosClient.patch(`/departments/${id}/`, payload);
export const deleteDepartment = (id) => axiosClient.delete(`/departments/${id}/`);

export const listAttendance = (params) => axiosClient.get('/attendance/', { params });
export const createAttendance = (payload) =>
  axiosClient.post('/attendance/', payload);

export const listKpiWeights = () => axiosClient.get('/kpi-weights/');
export const updateKpiWeight = (id, payload) =>
  axiosClient.patch(`/kpi-weights/${id}/`, payload);
export const createKpiWeight = (payload) =>
  axiosClient.post('/kpi-weights/', payload);
