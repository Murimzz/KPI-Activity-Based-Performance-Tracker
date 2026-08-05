import { Link } from 'react-router-dom';

export default function ForgotPasswordPage() {
  return (
    <div className="auth-page">
      <div className="auth-panel">
        <h1 className="auth-heading">Forgot password</h1>
        <p className="auth-copy">
          Password reset email is not configured yet. Ask an administrator to reset
          your password with:
        </p>
        <pre className="code-block">python manage.py changepassword your@email.com</pre>
        <Link to="/login">Back to sign in</Link>
      </div>
    </div>
  );
}
