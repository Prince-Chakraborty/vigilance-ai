import React, { useEffect, useState } from 'react';
import { api } from '../api';

const SEVERITY_OPTIONS = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

export default function Violations() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading]       = useState(true);
  const [severity, setSeverity]     = useState('ALL');
  const [search, setSearch]         = useState('');
  const [searched, setSearched]     = useState(null);

  useEffect(() => {
    fetchViolations();
  }, [severity]);

  const fetchViolations = () => {
    setLoading(true);
    const params = { limit: 100 };
    if (severity !== 'ALL') params.severity = severity;
    api.getViolations(params)
      .then(setViolations)
      .finally(() => setLoading(false));
  };

  const handleSearch = async () => {
    if (!search.trim()) return;
    setLoading(true);
    try {
      const data = await api.searchByPlate(search.trim());
      setSearched(data);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearched(null);
    setSearch('');
    fetchViolations();
  };

  const displayData = searched ? searched.violations : violations;

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Violation Records</div>
          <div className="page-subtitle">All detected traffic violations</div>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap', alignItems: 'center' }}>
        {SEVERITY_OPTIONS.map(s => (
          <button
            key={s}
            className={`btn ${severity === s ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setSeverity(s); setSearched(null); }}
            style={{ padding: '6px 14px', fontSize: 12 }}
          >
            {s}
          </button>
        ))}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <input
            className="search-input"
            placeholder="Search by plate..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn btn-primary" onClick={handleSearch} style={{ padding: '8px 16px' }}>
            Search
          </button>
          {searched && (
            <button className="btn btn-secondary" onClick={handleClearSearch} style={{ padding: '8px 16px' }}>
              Clear
            </button>
          )}
        </div>
      </div>

      {searched && (
        <div style={{ background: '#1a1d27', border: '1px solid #f97316', borderRadius: 8, padding: '12px 16px', marginBottom: 16, fontSize: 13, color: '#f97316' }}>
          Found {searched.count} violation(s) for plate: <strong>{searched.plate}</strong>
        </div>
      )}

      <div className="table-wrap">
        {loading ? (
          <div className="loading">
            <div className="spinner" /> Loading violations...
          </div>
        ) : displayData.length === 0 ? (
          <div className="empty">
            <div className="empty-icon">✅</div>
            <div>No violations found</div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Timestamp</th>
                <th>Violation</th>
                <th>Severity</th>
                <th>Camera</th>
                <th>Location</th>
                <th>Plate</th>
                <th>Confidence</th>
                <th>Challan</th>
              </tr>
            </thead>
            <tbody>
              {displayData.map(v => (
                <tr key={v.id}>
                  <td style={{ fontFamily: 'monospace', color: '#f97316', fontSize: 11 }}>{v.incident_id}</td>
                  <td style={{ fontSize: 11 }}>{new Date(v.timestamp).toLocaleString()}</td>
                  <td>{v.violation_label}</td>
                  <td><span className={`badge badge-${v.severity}`}>{v.severity}</span></td>
                  <td style={{ fontFamily: 'monospace' }}>{v.camera_id}</td>
                  <td style={{ fontSize: 12 }}>{v.location}</td>
                  <td style={{ fontFamily: 'monospace', color: '#60a5fa' }}>{v.license_plate || '—'}</td>
                  <td>{(v.confidence * 100).toFixed(1)}%</td>
                  <td>
                    <span className={`badge ${v.challan_issued ? 'badge-PAID' : 'badge-CANCELLED'}`}>
                      {v.challan_issued ? 'ISSUED' : 'PENDING'}
                    </span>
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
