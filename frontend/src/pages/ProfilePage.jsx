import { useState } from 'react';
import { toast } from 'react-toastify';
import * as authApi from '../api/authApi';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/helpers';

export default function ProfilePage() {
  const { user, refreshProfile } = useAuth();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const onChangePassword = async (e) => {
    e.preventDefault();
    try {
      await authApi.changePassword(oldPassword, newPassword);
      toast.success('Password updated');
      setOldPassword('');
      setNewPassword('');
      refreshProfile();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Profile</h2>
      </div>
      <div className="detail-grid">
        <div className="panel">
          <h3 className="panel-title">Account</h3>
          <p>
            <strong>Name:</strong> {user?.first_name} {user?.last_name}
          </p>
          <p>
            <strong>Email:</strong> {user?.email}
          </p>
          <p>
            <strong>Role:</strong> {user?.role}
          </p>
          <p>
            <strong>Employee/intern no.:</strong> {user?.employee_or_intern_number}
          </p>
          <p>
            <strong>Department:</strong> {user?.department?.name || '—'}
          </p>
        </div>
        <div className="panel">
          <h3 className="panel-title">Change password</h3>
          <form onSubmit={onChangePassword}>
            <div className="mb-3">
              <label className="form-label" htmlFor="old">
                Current password
              </label>
              <input
                id="old"
                type="password"
                className="form-control"
                required
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="new">
                New password
              </label>
              <input
                id="new"
                type="password"
                className="form-control"
                required
                minLength={8}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Update password
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
