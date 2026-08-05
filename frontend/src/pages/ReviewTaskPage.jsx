import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import * as taskApi from '../api/taskApi';
import LoadingState, { ErrorState } from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function ReviewTaskPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    supervisor_quality_rating: 4,
    supervisor_accuracy_rating: 4,
    supervisor_timeliness_rating: '',
    supervisor_comments: '',
  });

  useEffect(() => {
    (async () => {
      try {
        const { data } = await taskApi.getTask(id);
        setTask(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const setField = (key, value) => setForm((p) => ({ ...p, [key]: value }));

  const payload = () => ({
    supervisor_quality_rating: Number(form.supervisor_quality_rating),
    supervisor_accuracy_rating: Number(form.supervisor_accuracy_rating),
    supervisor_timeliness_rating: form.supervisor_timeliness_rating
      ? Number(form.supervisor_timeliness_rating)
      : null,
    supervisor_comments: form.supervisor_comments,
  });

  const onApprove = async () => {
    setSaving(true);
    try {
      await taskApi.approveTask(id, payload());
      toast.success('Task approved — contributes to Contribution Score');
      navigate(`/tasks/${id}`);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const onReject = async () => {
    if (!form.supervisor_comments.trim()) {
      toast.error('Comments are required when rejecting');
      return;
    }
    setSaving(true);
    try {
      await taskApi.rejectTask(id, payload());
      toast.info('Task rejected — returned to assignee');
      navigate(`/tasks/${id}`);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!task) return null;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Review task</h2>
          <p className="page-sub">{task.title}</p>
        </div>
      </div>

      <div className="detail-grid">
        <div className="panel">
          <h3 className="panel-title">Submission</h3>
          <p>
            <strong>Assignee:</strong>{' '}
            {task.assigned_to
              ? `${task.assigned_to.first_name} ${task.assigned_to.last_name}`
              : '—'}
          </p>
          <p>
            <strong>Expected / actual output:</strong> {task.expected_output ?? '—'} /{' '}
            {task.actual_output ?? '—'}
          </p>
          <p>
            <strong>Expected / actual duration:</strong> {task.expected_duration_minutes ?? '—'} /{' '}
            {task.actual_duration_minutes ?? '—'} min
          </p>
          <p>{task.description}</p>
          <p>
            <strong>Challenges:</strong> {task.challenges_encountered || '—'}
          </p>
          <ul>
            {(task.evidence || []).map((ev) => (
              <li key={ev.id}>
                <a href={ev.file} target="_blank" rel="noreferrer">
                  {ev.file_name || 'Evidence'}
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div className="panel">
          <h3 className="panel-title">Supervisor review</h3>
          <div className="mb-3">
            <label className="form-label" htmlFor="quality">
              Quality rating (1–5)
            </label>
            <input
              id="quality"
              type="number"
              min="1"
              max="5"
              className="form-control"
              value={form.supervisor_quality_rating}
              onChange={(e) => setField('supervisor_quality_rating', e.target.value)}
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="accuracy">
              Accuracy rating (1–5)
            </label>
            <input
              id="accuracy"
              type="number"
              min="1"
              max="5"
              className="form-control"
              value={form.supervisor_accuracy_rating}
              onChange={(e) => setField('supervisor_accuracy_rating', e.target.value)}
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="timeliness">
              Timeliness rating (optional 1–5)
            </label>
            <input
              id="timeliness"
              type="number"
              min="1"
              max="5"
              className="form-control"
              value={form.supervisor_timeliness_rating}
              onChange={(e) => setField('supervisor_timeliness_rating', e.target.value)}
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="comments">
              Comments (required to reject)
            </label>
            <textarea
              id="comments"
              className="form-control"
              rows={4}
              value={form.supervisor_comments}
              onChange={(e) => setField('supervisor_comments', e.target.value)}
            />
          </div>
          <div className="d-flex gap-2">
            <button
              type="button"
              className="btn btn-success"
              disabled={saving}
              onClick={onApprove}
            >
              Approve
            </button>
            <button
              type="button"
              className="btn btn-danger"
              disabled={saving}
              onClick={onReject}
            >
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
