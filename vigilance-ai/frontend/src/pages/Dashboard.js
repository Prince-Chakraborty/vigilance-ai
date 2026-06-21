import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { api } from '../api';

const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH:     '#f97316',
  MEDIUM:   '#eab308',
  LOW:      '#22c55e',
};

export default function Dashboard() {
  const [stats, setStats]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getStats()
      .then(s => setStats(s))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="loading">
      <div className="spinner" />
      Loading dashboard...
    </div>
  );

  const violationTypeData = Object.entries(stats.violations_by_type || {}).map(
    ([name, value]) => ({
      name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value
    })
  );

  const severityData = Object.entries(stats.violations_by_severity || {}).map(
    ([name, value]) => ({ name, value, color: SEVERITY_COLORS[name] })
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">Traffic Command Dashboard</div>
          <div className="page-subtitle">Real-time violation monitoring — Bengaluru</div>
        </div>
        <div style={{ fontSize: '13px', color: '#64748b' }}>
          {new Date().toLocaleString()}
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-label">Total Violations</div>
          <div className="stat-card-value">{stats.total_violations}</div>
          <div className="stat-card-sub">All time records</div>
        </div>
        <div className="stat-card critical">
          <div className="stat-card-label">Critical</div>
          <div className="stat-card-value">{stats.violations_by_severity?.CRITICAL || 0}</div>
          <div className="stat-card-sub">Immediate action required</div>
        </div>
        <div className="stat-card high">
          <div className="stat-card-label">High Severity</div>
          <div className="stat-card-value">{stats.violations_by_severity?.HIGH || 0}</div>
          <div className="stat-card-sub">Priority enforcement</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">Challans Issued</div>
          <div className="stat-card-value">{stats.total_challans}</div>
          <div className="stat-card-sub">E-tickets generated</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <div className="card-title">Violations by Type</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={violationTypeData} margin={{ left: -10 }}>
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} angle={-20} textAnchor="end" height={50} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip
                contentStyle={{ background: '#1a1d27', border: '1px solid #2d3148', borderRadius: 8 }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Bar dataKey="value" fill="#f97316" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Severity Breakdown</div>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%" cy="50%"
                innerRadius={60} outerRadius={90}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
                labelLine={{ stroke: '#64748b' }}
              >
                {severityData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1a1d27', border: '1px solid #2d3148', borderRadius: 8 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-title">Top Violation Hotspots</div>
        {stats.top_locations.map((loc, i) => (
          <div key={i} style={{ marginBottom: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontSize: 13, color: '#cbd5e1' }}>📍 {loc.location}</span>
              <span style={{ fontSize: 13, color: '#f97316', fontWeight: 600 }}>{loc.count}</span>
            </div>
            <div style={{ background: '#151720', borderRadius: 4, height: 6 }}>
              <div style={{
                background: '#f97316',
                height: 6,
                borderRadius: 4,
                width: `${(loc.count / stats.total_violations) * 100}%`
              }} />
            </div>
          </div>
        ))}
      </div>

      <div className="table-wrap">
        <div className="table-header">
          <span style={{ fontWeight: 600, color: '#f1f5f9' }}>Recent Violations</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Incident ID</th>
              <th>Violation</th>
              <th>Severity</th>
              <th>Location</th>
              <th>Plate</th>
              <th>Confidence</th>
              <th>Challan</th>
            </tr>
          </thead>
          <tbody>
            {stats.recent_violations.map(v => (
              <tr key={v.id}>
                <td style={{ fontFamily: 'monospace', color: '#f97316' }}>{v.incident_id}</td>
                <td>{v.violation_label}</td>
                <td><span className={`badge badge-${v.severity}`}>{v.severity}</span></td>
                <td>{v.location}</td>
                <td style={{ fontFamily: 'monospace' }}>{v.license_plate || '—'}</td>
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
      </div>
    </div>
  );
}
