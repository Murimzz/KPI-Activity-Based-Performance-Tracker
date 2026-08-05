import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { toast } from 'react-toastify';
import * as dashboardApi from '../api/dashboardApi';
import * as reportApi from '../api/reportApi';
import MetricCard from '../components/dashboard/MetricCard';
import LoadingState, { ErrorState } from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

function fmt(v) {
  if (v === null || v === undefined) return '—';
  return Number(v).toFixed(2);
}

export default function PersonalDashboard() {
  const [data, setData] = useState(null);
  const [statusData, setStatusData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        const [summary, statusRes, catRes] = await Promise.all([
          dashboardApi.dashboardSummary(),
          reportApi.statusBreakdown(),
          reportApi.categoryBreakdown(),
        ]);
        if (!alive) return;
        setData(summary.data);
        setStatusData(
          (statusRes.data.breakdown || []).map((row) => ({
            status: row.status,
            count: row.count,
          })),
        );
        setCategoryData(
          (catRes.data.breakdown || []).map((row) => ({
            name: row.category__name || 'Uncategorized',
            count: row.count,
          })),
        );
      } catch (err) {
        if (alive) {
          setError(getErrorMessage(err));
          toast.error(getErrorMessage(err));
        }
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  if (loading) return <LoadingState label="Loading dashboard…" />;
  if (error) return <ErrorState message={error} />;

  const m = data?.metrics || {};
  const trend = [
    { label: 'Completion', value: Number(m.completion_rate || 0) },
    { label: 'Output', value: Number(m.output_achievement || 0) },
    { label: 'Efficiency', value: Number(m.time_efficiency || 0) },
    { label: 'Quality', value: Number(m.quality_score || 0) },
    { label: 'Accuracy', value: Number(m.accuracy_score || 0) },
    { label: 'Attendance', value: Number(m.attendance_score || 0) },
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Personal dashboard</h2>
          <p className="page-sub">
            Overall Activity Score (Contribution Score):{' '}
            <strong>{fmt(m.overall_activity_score)}</strong> —{' '}
            {m.performance_classification || 'N/A'}
          </p>
        </div>
        <Link to="/tasks/new" className="btn btn-primary">
          Add task
        </Link>
      </div>

      <div className="metric-grid">
        <MetricCard label="Overall Activity Score" value={fmt(m.overall_activity_score)} />
        <MetricCard label="Completion Rate" value={fmt(m.completion_rate)} />
        <MetricCard label="Output Achievement" value={fmt(m.output_achievement)} />
        <MetricCard label="Time Efficiency" value={fmt(m.time_efficiency)} />
        <MetricCard label="Quality Score" value={fmt(m.quality_score)} />
        <MetricCard label="Accuracy Score" value={fmt(m.accuracy_score)} />
        <MetricCard label="Attendance Score" value={fmt(m.attendance_score)} />
        <MetricCard label="Approved Tasks" value={m.approved_tasks} />
        <MetricCard label="Pending Tasks" value={m.pending_tasks} />
        <MetricCard label="Rejected Tasks" value={m.rejected_tasks} />
        <MetricCard label="Total Hours" value={fmt(m.total_hours)} />
      </div>

      <div className="chart-grid mt-4">
        <div className="panel">
          <h3 className="panel-title">Metric profile</h3>
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis domain={[0, 120]} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#0f6e56" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel">
          <h3 className="panel-title">Tasks by status</h3>
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="status" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#1d4e89" name="Tasks" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel">
          <h3 className="panel-title">Tasks by category</h3>
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" hide={categoryData.length > 4} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#c45c26" name="Tasks" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="panel mt-4">
        <h3 className="panel-title">Recent tasks</h3>
        <div className="table-responsive">
          <table className="table table-sm align-middle">
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
                <th>Category</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {(data?.recent_tasks || []).map((task) => (
                <tr key={task.id}>
                  <td>{task.title}</td>
                  <td>
                    <span className={`status-pill status-${task.status?.toLowerCase()}`}>
                      {task.status}
                    </span>
                  </td>
                  <td>{task.category?.name || '—'}</td>
                  <td>
                    <Link to={`/tasks/${task.id}`}>Open</Link>
                  </td>
                </tr>
              ))}
              {!data?.recent_tasks?.length ? (
                <tr>
                  <td colSpan={4} className="text-muted">
                    No recent tasks.
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
