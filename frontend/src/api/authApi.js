import axiosClient from './axiosClient';

export const login = (email, password) =>
  axiosClient.post('/auth/login/', { email, password });

export const register = (payload) => axiosClient.post('/auth/register/', payload);

export const fetchMe = () => axiosClient.get('/auth/me/');

export const changePassword = (old_password, new_password) =>
  axiosClient.post('/auth/change-password/', { old_password, new_password });

export const refreshToken = (refresh) =>
  axiosClient.post('/auth/token/refresh/', { refresh });
