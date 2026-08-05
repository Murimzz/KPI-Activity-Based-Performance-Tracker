export const ROLES = {
  INTERN: 'INTERN',
  STAFF: 'STAFF',
  SUPERVISOR: 'SUPERVISOR',
  ADMIN: 'ADMIN',
};

export function isStaffLike(role) {
  return role === ROLES.INTERN || role === ROLES.STAFF;
}

export function isSupervisorLike(role) {
  return role === ROLES.SUPERVISOR || role === ROLES.ADMIN;
}

export function homePathForRole(role) {
  if (role === ROLES.ADMIN) return '/admin';
  if (role === ROLES.SUPERVISOR) return '/supervisor';
  return '/dashboard';
}

export function getErrorMessage(error, fallback = 'Something went wrong.') {
  const data = error?.response?.data;
  if (!data) return error?.message || fallback;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (typeof data === 'object') {
    const firstKey = Object.keys(data)[0];
    const val = data[firstKey];
    if (Array.isArray(val)) return `${firstKey}: ${val[0]}`;
    if (typeof val === 'string') return `${firstKey}: ${val}`;
  }
  return fallback;
}
