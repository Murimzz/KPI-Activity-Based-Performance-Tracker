import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import * as taskApi from '../api/taskApi';
import ConfirmDialog from '../components/common/ConfirmDialog';
import LoadingState, { ErrorState } from '../components/common/States';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage, isSupervisorLike, ROLES } from '../utils/helpers';

export default function TaskDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [file, setFile] = useState(null);
  const [confirmSubmit, setConfirmSubmit] = useState(false);

  const load = async () => {
    try {
      setLoading(true);
      const { data } = await taskApi.getTask(id);
      setTask(data);
      setError('');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const canEdit =
    task &&
    task.assigned_to?.id === user.id &&
    ['DRAFT', 'REJECTED'].includes(task.status);

  const canSubmit = canEdit;
  const canReview =
    task &&
    task.status === 'PENDING' &&
    isSupervisorLike(user.role) &&
    task.assigned_to?.id !== user.id;

  const onSubmit = async () => {
    try {
      const { data } = await taskApi.submitTask(id);
      setTask(data);
      toast.success('Task submitted for review');
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setConfirmSubmit(false);
    }
  };

  const onUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', 'Supporting evidence');
    try {
      await taskApi.uploadEvidence(id, formData);
      toast.success('Evidence uploaded');
      setFile(null);
      load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!task) return null;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">{task.title}</h2>
          <p className="page-sub">
            <span className={`status-pill status-${task.status?.toLowerCase()}`}>
              {task.status}
            </span>
          </p>
        </div>
        <div className="d-flex gap-2 flex-wrap">
          {canEdit ? (
            <Link to={`/tasks/${task.id}/edit`} className="btn btn-outline-primary">
              Edit
            </Link>
          ) : null}
          {canSubmit ? (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setConfirmSubmit(true)}
            >
              Submit for review
            </button>
          ) : null}
          {canReview ? (
            <Link to={`/tasks/${task.id}/review`} className="btn btn-primary">
              Review
            </Link>
          ) : null}
          <button type="button" className="btn btn-outline-secondary" onClick={() => navigate(-1)}>
            Back
          </button>
        </div>
      </div>

      <div className="detail-grid">
        <div className="panel">
          <h3 className="panel-title">Details</h3>
          <dl className="detail-list">
            <div>
              <dt>Assignee</dt>
              <dd>
                {task.assigned_to
                  ? `${task.assigned_to.first_name} ${task.assigned_to.last_name}`
                  : '—'}
              </dd>
            </div>
            <div>
              <dt>Supervisor</dt>
              <dd>
                {task.supervisor
                  ? `${task.supervisor.first_name} ${task.supervisor.last_name}`
                  : '—'}
              </dd>
            </div>
            <div>
              <dt>Category</dt>
              <dd>{task.category?.name || '—'}</dd>
            </div>
            <div>
              <dt>Expected / actual output</dt>
              <dd>
                {task.expected_output ?? '—'} / {task.actual_output ?? '—'}
              </dd>
            </div>
            <div>
              <dt>Expected / actual duration</dt>
              <dd>
                {task.expected_duration_minutes ?? '—'} / {task.actual_duration_minutes ?? '—'} min
              </dd>
            </div>
            <div>
              <dt>Dates</dt>
              <dd>
                Assigned {task.date_assigned || '—'} · Due {task.due_date || '—'} · Performed{' '}
                {task.date_performed || '—'}
              </dd>
            </div>
          </dl>
          <p className="mt-3">{task.description || 'No description.'}</p>
          {task.challenges_encountered ? (
            <p>
              <strong>Challenges:</strong> {task.challenges_encountered}
            </p>
          ) : null}
          {task.user_comments ? (
            <p>
              <strong>User comments:</strong> {task.user_comments}
            </p>
          ) : null}
          {task.supervisor_comments ? (
            <p>
              <strong>Supervisor comments:</strong> {task.supervisor_comments}
            </p>
          ) : null}
        </div>

        <div className="panel">
          <h3 className="panel-title">Evidence</h3>
          <ul className="list-unstyled">
            {(task.evidence || []).map((ev) => (
              <li key={ev.id} className="mb-2">
                <a href={ev.file} target="_blank" rel="noreferrer">
                  {ev.file_name || 'File'}
                </a>
                {ev.description ? <span className="text-muted"> — {ev.description}</span> : null}
              </li>
            ))}
            {!task.evidence?.length ? <li className="text-muted">No evidence yet.</li> : null}
          </ul>
          {(canEdit || user.role === ROLES.ADMIN) && (
            <form onSubmit={onUpload} className="mt-3">
              <label className="form-label" htmlFor="evidence">
                Upload evidence (PDF, JPG, PNG, DOCX, XLSX)
              </label>
              <input
                id="evidence"
                type="file"
                className="form-control"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <button type="submit" className="btn btn-sm btn-outline-primary mt-2" disabled={!file}>
                Upload
              </button>
            </form>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={confirmSubmit}
        title="Submit task?"
        message="This will send the task to your supervisor for review."
        confirmLabel="Submit"
        onCancel={() => setConfirmSubmit(false)}
        onConfirm={onSubmit}
      />
    </div>
  );
}
