import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import * as adminApi from '../api/adminApi';
import * as dashboardApi from '../api/dashboardApi';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function TeamPage({ mode = 'members' }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        if (mode === 'performance') {
          const { data } = await dashboardApi.dashboardTeam();
          setRows(data.members || []);
        } else {
          const { data } = await adminApi.myTeam();
          setRows(data.results || data);
        }
      } catch (err) {
        toast.error(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [mode]);

  if (loading) return <LoadingState />;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">
          {mode === 'performance' ? 'Team performance' : 'Team members'}
        </h2>
      </div>
      <div className="panel">
        <table className="table align-middle">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              {mode === 'performance' ? (
                <>
                  <th>Score</th>
                  <th>Class</th>
                </>
              ) : (
                <>
                  <th>Role</th>
                  <th>Department</th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {mode === 'performance'
              ? rows.map((m) => (
                  <tr key={m.user.id}>
                    <td>{m.user.full_name}</td>
                    <td>{m.user.email}</td>
                    <td>{Number(m.metrics.overall_activity_score).toFixed(2)}</td>
                    <td>{m.metrics.performance_classification}</td>
                  </tr>
                ))
              : rows.map((u) => (
                  <tr key={u.id}>
                    <td>
                      {u.first_name} {u.last_name}
                    </td>
                    <td>{u.email}</td>
                    <td>{u.role}</td>
                    <td>{u.department?.name || '—'}</td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
