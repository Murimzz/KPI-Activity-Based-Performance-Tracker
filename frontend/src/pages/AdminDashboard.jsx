import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import * as adminApi from '../api/adminApi';
import * as dashboardApi from '../api/dashboardApi';
import * as taskApi from '../api/taskApi';
import MetricCard from '../components/dashboard/MetricCard';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function AdminDashboard() {
  const [stats, setStats] = useState({ users: 0, depts: 0, categories: 0, pending: 0 });
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [users, depts, cats, pending, teamRes] = await Promise.all([
          adminApi.listUsers(),
          adminApi.listDepartments(),
          taskApi.listCategories(),
          taskApi.pendingReview(),
          dashboardApi.dashboardTeam(),
        ]);
        setStats({
          users: (users.data.results || users.data).length,
          depts: (depts.data.results || depts.data).length,
          categories: (cats.data.results || cats.data).length,
          pending: (pending.data.results || pending.data).length,
        });
        setTeam(teamRes.data);
      } catch (err) {
        toast.error(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <LoadingState />;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Admin dashboard</h2>
          <p className="page-sub">Organization-wide Contribution Score overview</p>
        </div>
        <Link to="/admin/users" className="btn btn-primary">
          Manage users
        </Link>
      </div>
      <div className="metric-grid">
        <MetricCard label="Users" value={stats.users} />
        <MetricCard label="Departments" value={stats.depts} />
        <MetricCard label="Categories" value={stats.categories} />
        <MetricCard label="Pending reviews" value={stats.pending} />
        <MetricCard label="Tracked people" value={team?.team_size ?? 0} />
      </div>
    </div>
  );
}
