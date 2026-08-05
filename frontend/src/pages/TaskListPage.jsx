import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import * as taskApi from '../api/taskApi';
import LoadingState, { EmptyState, ErrorState } from '../components/common/States';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage, isSupervisorLike } from '../utils/helpers';

export default function TaskListPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      setLoading(true);
      const params = status ? { status } : {};
      const { data } = isSupervisorLike(user.role)
        ? await taskApi.listTasks(params)
        : await taskApi.myTasks(params);
      setTasks(data.results || data);
      setError('');
    } catch (err) {
      setError(getErrorMessage(err));
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, user?.role]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Tasks</h2>
          <p className="page-sub">Draft → submit → supervisor review → approve/reject</p>
        </div>
        <Link to="/tasks/new" className="btn btn-primary">
          Add task
        </Link>
      </div>

      <div className="toolbar mb-3">
        <label htmlFor="statusFilter" className="form-label me-2 mb-0">
          Status
        </label>
        <select
          id="statusFilter"
          className="form-select form-select-sm w-auto"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All</option>
          {['DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'COMPLETED', 'CANCELLED'].map(
            (s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ),
          )}
        </select>
      </div>

      {!tasks.length ? (
        <EmptyState title="No tasks" message="Create a task to get started." />
      ) : (
        <div className="panel">
          <div className="table-responsive">
            <table className="table align-middle">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Assignee</th>
                  <th>Status</th>
                  <th>Due</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.id}>
                    <td>{task.title}</td>
                    <td>
                      {task.assigned_to
                        ? `${task.assigned_to.first_name} ${task.assigned_to.last_name}`
                        : '—'}
                    </td>
                    <td>
                      <span className={`status-pill status-${task.status?.toLowerCase()}`}>
                        {task.status}
                      </span>
                    </td>
                    <td>{task.due_date || '—'}</td>
                    <td className="text-end">
                      <Link to={`/tasks/${task.id}`} className="btn btn-sm btn-outline-primary">
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
