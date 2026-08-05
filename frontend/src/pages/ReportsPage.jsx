import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import * as reportApi from '../api/reportApi';
import LoadingState from '../components/common/States';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage, isSupervisorLike } from '../utils/helpers';

export default function ReportsPage() {
  const { user } = useAuth();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await reportApi.userReport(user.id);
        setReport(data);
      } catch (err) {
        toast.error(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [user?.id]);

  const downloadCsv = () => {
    const url = reportApi.exportCsvUrl();
    const access = localStorage.getItem('access_token');
    fetch(url, { headers: { Authorization: `Bearer ${access}` } })
      .then(async (res) => {
        if (!res.ok) throw new Error('Export failed');
        const blob = await res.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'contribution_scores.csv';
        link.click();
      })
      .catch((err) => toast.error(err.message));
  };

  if (loading) return <LoadingState />;

  const m = report?.metrics || {};

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Performance report</h2>
          <p className="page-sub">{report?.disclaimer}</p>
        </div>
        {isSupervisorLike(user.role) ? (
          <button type="button" className="btn btn-outline-primary" onClick={downloadCsv}>
            Export CSV
          </button>
        ) : null}
      </div>
      <div className="panel">
        <p>
          <strong>Period:</strong> {report?.reporting_period?.start} →{' '}
          {report?.reporting_period?.end}
        </p>
        <p>
          <strong>Overall Activity Score:</strong> {m.overall_activity_score} (
          {m.performance_classification})
        </p>
        <ul>
          <li>Completion: {m.completion_rate}</li>
          <li>Output: {m.output_achievement}</li>
          <li>Time efficiency: {m.time_efficiency}</li>
          <li>Quality: {m.quality_score}</li>
          <li>Accuracy: {m.accuracy_score}</li>
          <li>Attendance: {m.attendance_score}</li>
          <li>
            Tasks — approved {m.approved_tasks}, pending {m.pending_tasks}, rejected{' '}
            {m.rejected_tasks}
          </li>
        </ul>
      </div>
    </div>
  );
}
