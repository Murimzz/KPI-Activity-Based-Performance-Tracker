import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import * as taskApi from '../api/taskApi';
import { useAuth } from '../context/AuthContext';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

const empty = {
  title: '',
  description: '',
  category_id: '',
  date_assigned: new Date().toISOString().slice(0, 10),
  due_date: '',
  date_performed: '',
  start_time: '',
  end_time: '',
  expected_output: '',
  actual_output: '',
  expected_duration_minutes: '',
  actual_duration_minutes: '',
  difficulty_level: 'MEDIUM',
  challenges_encountered: '',
  user_comments: '',
};

function minutesBetween(start, end) {
  if (!start || !end) return '';
  const [sh, sm] = start.split(':').map(Number);
  const [eh, em] = end.split(':').map(Number);
  const diff = eh * 60 + em - (sh * 60 + sm);
  return diff > 0 ? String(diff) : '';
}

export default function TaskFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { user } = useAuth();
  const [form, setForm] = useState(empty);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    taskApi.listCategories({ active: true }).then(({ data }) => {
      setCategories(data.results || data);
    });
  }, []);

  useEffect(() => {
    if (!isEdit) return;
    (async () => {
      try {
        const { data } = await taskApi.getTask(id);
        setForm({
          title: data.title || '',
          description: data.description || '',
          category_id: data.category?.id || '',
          date_assigned: data.date_assigned || '',
          due_date: data.due_date || '',
          date_performed: data.date_performed || '',
          start_time: data.start_time ? data.start_time.slice(0, 5) : '',
          end_time: data.end_time ? data.end_time.slice(0, 5) : '',
          expected_output: data.expected_output ?? '',
          actual_output: data.actual_output ?? '',
          expected_duration_minutes: data.expected_duration_minutes ?? '',
          actual_duration_minutes: data.actual_duration_minutes ?? '',
          difficulty_level: data.difficulty_level || 'MEDIUM',
          challenges_encountered: data.challenges_encountered || '',
          user_comments: data.user_comments || '',
        });
      } catch (err) {
        toast.error(getErrorMessage(err));
        navigate('/tasks');
      } finally {
        setLoading(false);
      }
    })();
  }, [id, isEdit, navigate]);

  const autoDuration = useMemo(
    () => minutesBetween(form.start_time, form.end_time),
    [form.start_time, form.end_time],
  );

  const setField = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    if (form.end_time && form.start_time && form.end_time <= form.start_time) {
      toast.error('End time must be after start time');
      return;
    }
    if (form.due_date && form.date_assigned && form.due_date < form.date_assigned) {
      toast.error('Due date cannot be before assigned date');
      return;
    }

    const payload = {
      title: form.title,
      description: form.description,
      category_id: Number(form.category_id),
      assigned_to_id: user.id,
      date_assigned: form.date_assigned || null,
      due_date: form.due_date || null,
      date_performed: form.date_performed || null,
      start_time: form.start_time ? `${form.start_time}:00` : null,
      end_time: form.end_time ? `${form.end_time}:00` : null,
      expected_output: form.expected_output === '' ? null : form.expected_output,
      actual_output: form.actual_output === '' ? null : form.actual_output,
      expected_duration_minutes:
        form.expected_duration_minutes === ''
          ? null
          : Number(form.expected_duration_minutes),
      actual_duration_minutes:
        form.actual_duration_minutes === ''
          ? autoDuration
            ? Number(autoDuration)
            : null
          : Number(form.actual_duration_minutes),
      difficulty_level: form.difficulty_level,
      challenges_encountered: form.challenges_encountered,
      user_comments: form.user_comments,
    };

    setSaving(true);
    try {
      if (isEdit) {
        const { data } = await taskApi.updateTask(id, payload);
        toast.success('Task updated');
        navigate(`/tasks/${data.id}`);
      } else {
        const { data } = await taskApi.createTask(payload);
        toast.success('Task created as draft');
        navigate(`/tasks/${data.id}`);
      }
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not save task'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingState />;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">{isEdit ? 'Edit task' : 'Add task'}</h2>
      </div>
      <form className="panel form-panel" onSubmit={onSubmit}>
        <div className="row g-3">
          <div className="col-md-8">
            <label className="form-label" htmlFor="title">
              Title
            </label>
            <input
              id="title"
              className="form-control"
              required
              value={form.title}
              onChange={(e) => setField('title', e.target.value)}
            />
          </div>
          <div className="col-md-4">
            <label className="form-label" htmlFor="category">
              Category
            </label>
            <select
              id="category"
              className="form-select"
              required
              value={form.category_id}
              onChange={(e) => setField('category_id', e.target.value)}
            >
              <option value="">Select…</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-12">
            <label className="form-label" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              className="form-control"
              rows={3}
              value={form.description}
              onChange={(e) => setField('description', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="date_assigned">
              Date assigned
            </label>
            <input
              id="date_assigned"
              type="date"
              className="form-control"
              value={form.date_assigned}
              onChange={(e) => setField('date_assigned', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="due_date">
              Due date
            </label>
            <input
              id="due_date"
              type="date"
              className="form-control"
              value={form.due_date}
              onChange={(e) => setField('due_date', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="date_performed">
              Date performed
            </label>
            <input
              id="date_performed"
              type="date"
              className="form-control"
              value={form.date_performed}
              onChange={(e) => setField('date_performed', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="difficulty">
              Difficulty
            </label>
            <select
              id="difficulty"
              className="form-select"
              value={form.difficulty_level}
              onChange={(e) => setField('difficulty_level', e.target.value)}
            >
              {['LOW', 'MEDIUM', 'HIGH', 'COMPLEX'].map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="start_time">
              Start time
            </label>
            <input
              id="start_time"
              type="time"
              className="form-control"
              value={form.start_time}
              onChange={(e) => setField('start_time', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="end_time">
              End time
            </label>
            <input
              id="end_time"
              type="time"
              className="form-control"
              value={form.end_time}
              onChange={(e) => setField('end_time', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="expected_output">
              Expected output
            </label>
            <input
              id="expected_output"
              type="number"
              min="0"
              step="0.01"
              className="form-control"
              value={form.expected_output}
              onChange={(e) => setField('expected_output', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="actual_output">
              Actual output
            </label>
            <input
              id="actual_output"
              type="number"
              min="0"
              step="0.01"
              className="form-control"
              value={form.actual_output}
              onChange={(e) => setField('actual_output', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="expected_duration">
              Expected duration (min)
            </label>
            <input
              id="expected_duration"
              type="number"
              min="0"
              className="form-control"
              value={form.expected_duration_minutes}
              onChange={(e) => setField('expected_duration_minutes', e.target.value)}
            />
          </div>
          <div className="col-md-3">
            <label className="form-label" htmlFor="actual_duration">
              Actual duration (min)
            </label>
            <input
              id="actual_duration"
              type="number"
              min="0"
              className="form-control"
              value={form.actual_duration_minutes || autoDuration}
              onChange={(e) => setField('actual_duration_minutes', e.target.value)}
              placeholder={autoDuration ? `Auto: ${autoDuration}` : ''}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label" htmlFor="challenges">
              Challenges encountered
            </label>
            <textarea
              id="challenges"
              className="form-control"
              rows={2}
              value={form.challenges_encountered}
              onChange={(e) => setField('challenges_encountered', e.target.value)}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label" htmlFor="comments">
              User comments
            </label>
            <textarea
              id="comments"
              className="form-control"
              rows={2}
              value={form.user_comments}
              onChange={(e) => setField('user_comments', e.target.value)}
            />
          </div>
        </div>
        <div className="mt-4 d-flex gap-2">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving…' : 'Save draft'}
          </button>
          <button
            type="button"
            className="btn btn-outline-secondary"
            onClick={() => navigate(-1)}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
