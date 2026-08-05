import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import * as adminApi from '../api/adminApi';
import LoadingState from '../components/common/States';
import { getErrorMessage } from '../utils/helpers';

export default function KpiWeightsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const { data } = await adminApi.listKpiWeights();
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

  const onSave = async (row) => {
    try {
      await adminApi.updateKpiWeight(row.id, {
        weight_percentage: row.weight_percentage,
        active: row.active,
        name: row.name,
      });
      toast.success('Weight updated (active weights must total 100%)');
      load();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  };

  if (loading) return <LoadingState />;

  const total = rows
    .filter((r) => r.active)
    .reduce((sum, r) => sum + Number(r.weight_percentage), 0);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">KPI weights</h2>
          <p className="page-sub">Active total: {total.toFixed(2)}% (must be 100%)</p>
        </div>
      </div>
      <div className="panel">
        <table className="table align-middle">
          <thead>
            <tr>
              <th>Name</th>
              <th>Key</th>
              <th>Weight %</th>
              <th>Active</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={row.id}>
                <td>{row.name}</td>
                <td>
                  <code>{row.metric_key}</code>
                </td>
                <td style={{ maxWidth: 120 }}>
                  <input
                    type="number"
                    className="form-control form-control-sm"
                    value={row.weight_percentage}
                    onChange={(e) => {
                      const next = [...rows];
                      next[idx] = { ...row, weight_percentage: e.target.value };
                      setRows(next);
                    }}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={row.active}
                    onChange={(e) => {
                      const next = [...rows];
                      next[idx] = { ...row, active: e.target.checked };
                      setRows(next);
                    }}
                  />
                </td>
                <td>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => onSave(row)}
                  >
                    Save
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
