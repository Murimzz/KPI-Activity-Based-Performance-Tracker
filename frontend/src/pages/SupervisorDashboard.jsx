import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import * as dashboardApi from '../api/dashboardApi';
import * as taskApi from '../api/taskApi';
import MetricCard from '../components/dashboard/MetricCard';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function SupervisorDashboard() {
  const [team, setTeam] = useState(null);
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [teamRes, pendingRes] = await Promise.all([
          dashboardApi.dashboardTeam(),
          taskApi.pendingReview(),
        ]);
        setTeam(teamRes.data);
        setPending(pendingRes.data.results || pendingRes.data);
      } catch (err) {
        toast.error(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <LoadingState />;

  const avg =
    team?.members?.length
      ? (
          team.members.reduce(
            (sum, m) => sum + Number(m.metrics?.overall_activity_score || 0),
            0,
          ) / team.members.length
        ).toFixed(2)
      : '—';

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Supervisor dashboard</h2>
          <p className="page-sub">Team Contribution Scores (not official appraisals)</p>
        </div>
        <Link to="/supervisor/pending" className="btn btn-primary">
          Pending reviews ({pending.length})
        </Link>
      </div>

      <div className="metric-grid">
        <MetricCard label="Team size" value={team?.team_size ?? 0} />
        <MetricCard label="Avg Activity Score" value={avg} />
        <MetricCard label="Pending reviews" value={pending.length} />
      </div>

      <div className="panel mt-4">
        <h3 className="panel-title">Team members</h3>
        <div className="table-responsive">
          <table className="table align-middle">
            <thead>
              <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Overall score</th>
                <th>Classification</th>
                <th>Approved</th>
              </tr>
            </thead>
            <tbody>
              {(team?.members || []).map((m) => (
                <tr key={m.user.id}>
                  <td>{m.user.full_name}</td>
                  <td>{m.user.role}</td>
                  <td>{Number(m.metrics.overall_activity_score).toFixed(2)}</td>
                  <td>{m.metrics.performance_classification}</td>
                  <td>{m.metrics.approved_tasks}</td>
                </tr>
              ))}
              {!team?.members?.length ? (
                <tr>
                  <td colSpan={5} className="text-muted">
                    No supervised users yet. Assign supervisors in Admin → Users.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
