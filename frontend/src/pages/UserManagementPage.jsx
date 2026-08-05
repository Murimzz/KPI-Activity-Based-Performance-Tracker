import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import * as adminApi from '../api/adminApi';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    role: 'INTERN',
    employee_or_intern_number: '',
    department_id: '',
    supervisor_id: '',
  });

  const load = async () => {
    try {
      const [u, d] = await Promise.all([adminApi.listUsers(), adminApi.listDepartments()]);
      setUsers(u.data.results || u.data);
      setDepartments(d.data.results || d.data);
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
      await adminApi.createUser({
        ...form,
        department_id: form.department_id ? Number(form.department_id) : null,
        supervisor_id: form.supervisor_id ? Number(form.supervisor_id) : null,
      });
      toast.success('User created');
      setForm({
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        role: 'INTERN',
        employee_or_intern_number: '',
        department_id: '',
        supervisor_id: '',
      });
      load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  const toggleActive = async (user) => {
    try {
      await adminApi.updateUser(user.id, { is_active: !user.is_active });
      toast.success(user.is_active ? 'User deactivated' : 'User activated');
      load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  if (loading) return <LoadingState />;

  const supervisors = users.filter((u) => u.role === 'SUPERVISOR' || u.role === 'ADMIN');

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">User management</h2>
      </div>

      <form className="panel mb-4" onSubmit={onCreate}>
        <h3 className="panel-title">Add user</h3>
        <div className="row g-2">
          <div className="col-md-3">
            <input
              className="form-control"
              placeholder="First name"
              required
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
            />
          </div>
          <div className="col-md-3">
            <input
              className="form-control"
              placeholder="Last name"
              required
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
            />
          </div>
          <div className="col-md-3">
            <input
              className="form-control"
              type="email"
              placeholder="Email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div className="col-md-3">
            <input
              className="form-control"
              type="password"
              placeholder="Password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          <div className="col-md-3">
            <input
              className="form-control"
              placeholder="Employee/intern no."
              required
              value={form.employee_or_intern_number}
              onChange={(e) =>
                setForm({ ...form, employee_or_intern_number: e.target.value })
              }
            />
          </div>
          <div className="col-md-3">
            <select
              className="form-select"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              {['INTERN', 'STAFF', 'SUPERVISOR', 'ADMIN'].map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-3">
            <select
              className="form-select"
              value={form.department_id}
              onChange={(e) => setForm({ ...form, department_id: e.target.value })}
            >
              <option value="">Department</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-3">
            <select
              className="form-select"
              value={form.supervisor_id}
              onChange={(e) => setForm({ ...form, supervisor_id: e.target.value })}
            >
              <option value="">Supervisor</option>
              {supervisors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.first_name} {s.last_name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <button type="submit" className="btn btn-primary mt-3">
          Create user
        </button>
      </form>

      <div className="panel">
        <table className="table align-middle">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Active</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>
                  {u.first_name} {u.last_name}
                </td>
                <td>{u.email}</td>
                <td>{u.role}</td>
                <td>{u.is_active ? 'Yes' : 'No'}</td>
                <td className="text-end">
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => toggleActive(u)}
                  >
                    {u.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
