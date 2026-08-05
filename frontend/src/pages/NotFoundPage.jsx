import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="auth-page">
      <div className="auth-panel">
        <h1 className="auth-heading">Page not found</h1>
        <p className="auth-copy">That route does not exist.</p>
        <Link to="/" className="btn btn-primary">
          Home
        </Link>
      </div>
    </div>
  );
}
