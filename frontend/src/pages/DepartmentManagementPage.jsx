import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import * as adminApi from '../api/adminApi';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function DepartmentManagementPage() {
  const [rows, setRows] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const { data } = await adminApi.listDepartments();
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
      await adminApi.createDepartment({ name, description });
      toast.success('Department created');
      setName('');
      setDescription('');
      load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  if (loading) return <LoadingState />;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Departments</h2>
      </div>
      <form className="panel mb-3" onSubmit={onCreate}>
        <div className="row g-2">
          <div className="col-md-4">
            <input
              className="form-control"
              placeholder="Name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="col-md-6">
            <input
              className="form-control"
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="col-md-2">
            <button className="btn btn-primary w-100" type="submit">
              Add
            </button>
          </div>
        </div>
      </form>
      <div className="panel">
        <ul className="list-group list-group-flush">
          {rows.map((d) => (
            <li key={d.id} className="list-group-item">
              <strong>{d.name}</strong>
              <div className="text-muted">{d.description}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
