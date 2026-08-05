import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { homePathForRole } from '../utils/helpers';

export default function UnauthorizedPage() {
  const { user } = useAuth();
  return (
    <div className="auth-page">
      <div className="auth-panel">
        <h1 className="auth-heading">Unauthorized</h1>
        <p className="auth-copy">You do not have permission to view this page.</p>
        <Link to={homePathForRole(user?.role)} className="btn btn-primary">
          Go to my dashboard
        </Link>
      </div>
    </div>
  );
}
