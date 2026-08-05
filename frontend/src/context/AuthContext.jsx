import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import * as authApi from '../api/authApi';
import { getErrorMessage } from '../utils/helpers';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('auth_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  const persistSession = useCallback((access, refresh, nextUser) => {
    // DEV: localStorage is convenient for development.
    // PRODUCTION: prefer HTTP-only secure cookies for tokens.
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('auth_user', JSON.stringify(nextUser));
    setUser(nextUser);
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('auth_user');
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    const access = localStorage.getItem('access_token');
    if (!access) {
      setUser(null);
      setLoading(false);
      return null;
    }
    try {
      const { data } = await authApi.fetchMe();
      localStorage.setItem('auth_user', JSON.stringify(data));
      setUser(data);
      return data;
    } catch {
      clearSession();
      return null;
    } finally {
      setLoading(false);
    }
  }, [clearSession]);

  useEffect(() => {
    refreshProfile();
  }, [refreshProfile]);

  const login = useCallback(
    async (email, password) => {
      const { data } = await authApi.login(email, password);
      persistSession(data.access, data.refresh, data.user);
      return data.user;
    },
    [persistSession],
  );

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      refreshProfile,
      getErrorMessage,
    }),
    [user, loading, login, logout, refreshProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
