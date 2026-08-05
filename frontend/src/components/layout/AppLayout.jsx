import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ROLES, homePathForRole } from '../../utils/helpers';

function navForRole(role) {
  if (role === ROLES.ADMIN) {
    return [
      { to: '/admin', label: 'Admin dashboard' },
      { to: '/admin/users', label: 'Users' },
      { to: '/admin/departments', label: 'Departments' },
      { to: '/admin/categories', label: 'Categories' },
      { to: '/admin/kpi-weights', label: 'KPI weights' },
      { to: '/tasks', label: 'All tasks' },
      { to: '/reports', label: 'Reports' },
      { to: '/profile', label: 'Profile' },
    ];
  }
  if (role === ROLES.SUPERVISOR) {
    return [
      { to: '/supervisor', label: 'Supervisor dashboard' },
      { to: '/supervisor/pending', label: 'Pending reviews' },
      { to: '/supervisor/team', label: 'Team' },
      { to: '/supervisor/performance', label: 'Team performance' },
      { to: '/tasks', label: 'Tasks' },
      { to: '/reports', label: 'Reports' },
      { to: '/profile', label: 'Profile' },
    ];
  }
  return [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/tasks', label: 'My tasks' },
    { to: '/tasks/new', label: 'Add task' },
    { to: '/reports', label: 'Performance' },
    { to: '/attendance', label: 'Attendance' },
    { to: '/profile', label: 'Profile' },
  ];
}

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const links = navForRole(user?.role);

  const onLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="brand-block">
          <NavLink to={homePathForRole(user?.role)} className="brand-title">
            Activity Performance
          </NavLink>
          <p className="brand-sub">Contribution Score tracker</p>
        </div>
        <nav className="side-nav" aria-label="Main">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/dashboard' || link.to === '/admin' || link.to === '/supervisor'}
              className={({ isActive }) =>
                isActive ? 'side-link active' : 'side-link'
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="side-footer">
          <p className="side-user mb-1">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="side-role mb-2">{user?.role}</p>
          <button type="button" className="btn btn-outline-light btn-sm w-100" onClick={onLogout}>
            Log out
          </button>
        </div>
      </aside>
      <div className="app-main">
        <header className="app-topbar">
          <div>
            <h1 className="page-kicker">Activity-Based Performance Tracker</h1>
            <p className="disclaimer mb-0">
              Scores shown are Contribution / Activity Performance Scores — not an
              official government performance appraisal.
            </p>
          </div>
        </header>
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
