import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import * as adminApi from '../api/adminApi';
import LoadingState from '../components/common/States';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/helpers';

export default function AttendancePage() {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    date: new Date().toISOString().slice(0, 10),
    status: 'PRESENT',
    check_in_time: '09:00',
    check_out_time: '17:00',
    notes: '',
  });

  const load = async () => {
    try {
      const { data } = await adminApi.listAttendance({ user: user.id });
      setRows(data.results || data);
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  const onCreate = async (e) => {
    e.preventDefault();
    try {
      await adminApi.createAttendance({
        date: form.date,
        status: form.status,
        check_in_time: form.check_in_time ? `${form.check_in_time}:00` : null,
        check_out_time: form.check_out_time ? `${form.check_out_time}:00` : null,
        notes: form.notes,
      });
      toast.success('Attendance recorded');
      load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  if (loading) return <LoadingState />;

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Attendance</h2>
      </div>
      <form className="panel mb-3" onSubmit={onCreate}>
        <div className="row g-2">
          <div className="col-md-3">
            <input
              type="date"
              className="form-control"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
            />
          </div>
          <div className="col-md-3">
            <select
              className="form-select"
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
            >
              {['PRESENT', 'ABSENT', 'LATE', 'OFFICIAL_DUTY', 'LEAVE'].map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="col-md-2">
            <input
              type="time"
              className="form-control"
              value={form.check_in_time}
              onChange={(e) => setForm({ ...form, check_in_time: e.target.value })}
            />
          </div>
          <div className="col-md-2">
            <input
              type="time"
              className="form-control"
              value={form.check_out_time}
              onChange={(e) => setForm({ ...form, check_out_time: e.target.value })}
            />
          </div>
          <div className="col-md-2">
            <button className="btn btn-primary w-100" type="submit">
              Save
            </button>
          </div>
        </div>
      </form>
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Status</th>
              <th>In</th>
              <th>Out</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.date}</td>
                <td>{r.status}</td>
                <td>{r.check_in_time || '—'}</td>
                <td>{r.check_out_time || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
