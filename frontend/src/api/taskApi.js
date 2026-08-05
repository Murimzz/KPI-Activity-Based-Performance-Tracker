import axiosClient from './axiosClient';

export const listTasks = (params) => axiosClient.get('/tasks/', { params });
export const myTasks = (params) => axiosClient.get('/tasks/my-tasks/', { params });
export const pendingReview = (params) =>
  axiosClient.get('/tasks/pending-review/', { params });
export const getTask = (id) => axiosClient.get(`/tasks/${id}/`);
export const createTask = (payload) => axiosClient.post('/tasks/', payload);
export const updateTask = (id, payload) => axiosClient.patch(`/tasks/${id}/`, payload);
export const deleteTask = (id) => axiosClient.delete(`/tasks/${id}/`);
export const submitTask = (id) => axiosClient.post(`/tasks/${id}/submit/`);
export const approveTask = (id, payload) =>
  axiosClient.post(`/tasks/${id}/approve/`, payload);
export const rejectTask = (id, payload) =>
  axiosClient.post(`/tasks/${id}/reject/`, payload);
export const uploadEvidence = (id, formData) =>
  axiosClient.post(`/tasks/${id}/evidence/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const listCategories = (params) =>
  axiosClient.get('/task-categories/', { params });
export const createCategory = (payload) =>
  axiosClient.post('/task-categories/', payload);
export const updateCategory = (id, payload) =>
  axiosClient.patch(`/task-categories/${id}/`, payload);
export const deleteCategory = (id) => axiosClient.delete(`/task-categories/${id}/`);
