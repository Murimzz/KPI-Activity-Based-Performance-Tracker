import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import * as taskApi from '../api/taskApi';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function CategoryManagementPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    name: '',
    description: '',
    default_expected_output: 1,
    default_expected_duration_minutes: 60,
    difficulty_level: 'MEDIUM',
  });

  const load = async () => {
    try {
      const { data } = await taskApi.listCategories();
      setRows(data.results || data);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    try {
      await taskApi.createCategory(form);
      toast.success('Category created');
      setForm({
        name: '',
        description: '',
        default_expected_output: 1,
        default_expected_duration_minutes: 60,
        difficulty_level: 'MEDIUM',
      });
      load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  if (loading) return <LoadingState />;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Task categories</h2>
      </div>
      <form className="panel mb-3" onSubmit={onCreate}>
        <div className="row g-2">
          <div className="col-md-3">
            <input
              className="form-control"
              placeholder="Name"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="col-md-3">
            <input
              className="form-control"
              type="number"
              min="0"
              step="0.01"
              value={form.default_expected_output}
              onChange={(e) =>
                setForm({ ...form, default_expected_output: e.target.value })
              }
            />
          </div>
          <div className="col-md-2">
            <input
              className="form-control"
              type="number"
              min="1"
              value={form.default_expected_duration_minutes}
              onChange={(e) =>
                setForm({
                  ...form,
                  default_expected_duration_minutes: e.target.value,
                })
              }
            />
          </div>
          <div className="col-md-2">
            <select
              className="form-select"
              value={form.difficulty_level}
              onChange={(e) => setForm({ ...form, difficulty_level: e.target.value })}
            >
              {['LOW', 'MEDIUM', 'HIGH', 'COMPLEX'].map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </div>
          <div className="col-md-2">
            <button className="btn btn-primary w-100" type="submit">
              Add
            </button>
          </div>
        </div>
      </form>
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Output</th>
              <th>Duration</th>
              <th>Difficulty</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.default_expected_output}</td>
                <td>{c.default_expected_duration_minutes}</td>
                <td>{c.difficulty_level}</td>
                <td>{c.active ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
