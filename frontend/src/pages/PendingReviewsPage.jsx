import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import * as taskApi from '../api/taskApi';
import LoadingState, { EmptyState } from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function PendingReviewsPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await taskApi.pendingReview();
        setTasks(data.results || data);
      } catch (err) {
        toast.error(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <LoadingState />;
  if (!tasks.length) {
    return <EmptyState title="No pending reviews" message="You're all caught up." />;
  }

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Pending reviews</h2>
      </div>
      <div className="panel">
        <table className="table align-middle">
          <thead>
            <tr>
              <th>Title</th>
              <th>Assignee</th>
              <th>Submitted</th>
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
                <td>{task.submitted_at ? new Date(task.submitted_at).toLocaleString() : '—'}</td>
                <td className="text-end">
                  <Link to={`/tasks/${task.id}/review`} className="btn btn-sm btn-primary">
                    Review
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
