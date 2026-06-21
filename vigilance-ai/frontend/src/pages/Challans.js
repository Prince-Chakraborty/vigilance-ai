import React, { useEffect, useState } from 'react';
import { api } from '../api';

export default function Challans() {
  const [challans, setChallans]   = useState([]);
  const [summary, setSummary]     = useState(null);
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    Promise.all([api.getChallans({ limit: 100 }), api.getChallanSummary()])
      .then(([c, s]) => { setChallans(c); setSummary(s); })
      .finally(() => setLoading(false));
  }, []);

  const handleStatusUpdate = async (challanId, status) => {
    await api.updateChallanStatus(challanId, status);
    const [c, s] = await Promise.all([
      api.getChallans({ limit: 100 }),
      api.getChallanSummary()
    ]);
    setChallans(c);
    setSummary(s);
  };

  const fineColor = (amount) => {
    if (amount >= 5000) return '#ef4444';
    if (amount >= 2000) return '#f97316';
    if (amount >= 1000) return '#eab308';
    return '#22c55e';
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Challan Management</div>
          <div className="page-subtitle">Issued e-tickets and fine collection</div>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="stats-grid" style={{ marginBottom: 24 }}>
          <div className="stat-card">
            <div className="stat-card-label">Total Challans</div>
            <div className="stat-card-value">{summary.total_challans}</div>
            <div className="stat-card-sub">All issued tickets</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">Total Fines Issued</div>
            <div className="stat-card-value" style={{ fontSize: 22 }}>
              ₹{summary.total_issued_inr?.toLocaleString()}
            </div>
            <div className="stat-card-sub">Cumulative amount</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">Collected</div>
            <div className="stat-card-value" style={{ fontSize: 22, color: '#22c55e' }}>
              ₹{summary.total_collected_inr?.toLocaleString()}
            </div>
            <div className="stat-card-sub">Paid challans</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">Pending</div>
            <div className="stat-card-value" style={{ fontSize: 22, color: '#f97316' }}>
              ₹{summary.total_pending_inr?.toLocaleString()}
            </div>
            <div className="stat-card-sub">Outstanding fines</div>
          </div>
        </div>
      )}

      <div className="table-wrap">
        {loading ? (
          <div className="loading">
            <div className="spinner" /> Loading challans...
          </div>
        ) : challans.length === 0 ? (
          <div className="empty">
            <div className="empty-icon">📋</div>
            <div>No challans issued yet</div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Challan ID</th>
                <th>Timestamp</th>
                <th>Plate</th>
                <th>Violation</th>
                <th>Severity</th>
                <th>Fine (INR)</th>
                <th>Location</th>
                <th>Camera</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {challans.map(c => (
                <tr key={c.challan_id}>
                  <td style={{ fontFamily: 'monospace', color: '#f97316', fontSize: 11 }}>{c.challan_id}</td>
                  <td style={{ fontSize: 11 }}>{new Date(c.timestamp).toLocaleString()}</td>
                  <td style={{ fontFamily: 'monospace', color: '#60a5fa', fontWeight: 600 }}>{c.license_plate}</td>
                  <td style={{ fontSize: 12 }}>{c.violation_label}</td>
                  <td><span className={`badge badge-${c.severity}`}>{c.severity}</span></td>
                  <td style={{ color: fineColor(c.fine_amount), fontWeight: 700 }}>
                    ₹{c.fine_amount?.toLocaleString()}
                  </td>
                  <td style={{ fontSize: 12 }}>{c.location}</td>
                  <td style={{ fontFamily: 'monospace' }}>{c.camera_id}</td>
                  <td><span className={`badge badge-${c.status}`}>{c.status}</span></td>
                  <td>
                    {c.status === 'ISSUED' && (
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button
                          className="btn btn-primary"
                          style={{ padding: '4px 10px', fontSize: 11 }}
                          onClick={() => handleStatusUpdate(c.challan_id, 'PAID')}
                        >
                          Mark Paid
                        </button>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '4px 10px', fontSize: 11 }}
                          onClick={() => handleStatusUpdate(c.challan_id, 'CANCELLED')}
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                    {c.status !== 'ISSUED' && (
                      <span style={{ fontSize: 12, color: '#64748b' }}>—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
