import React from 'react';

const navItems = [
  { id: 'dashboard',  icon: '📊', label: 'Dashboard'  },
  { id: 'analyze',    icon: '🔍', label: 'Analyze'    },
  { id: 'violations', icon: '⚠️',  label: 'Violations' },
  { id: 'challans',   icon: '📋', label: 'Challans'   },
];

export default function Sidebar({ active, onNav }) {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <h1>VIGILANCE AI</h1>
        <p>AI Traffic Enforcement</p>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <div
            key={item.id}
            className={`nav-item ${active === item.id ? 'active' : ''}`}
            onClick={() => onNav(item.id)}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>
      <div style={{ padding: '24px', borderTop: '1px solid #2d3148' }}>
        <div style={{ fontSize: '11px', color: '#64748b' }}>
          <div>Bengaluru, Karnataka</div>
          <div style={{ marginTop: '4px', color: '#22c55e' }}>System Online</div>
        </div>
      </div>
    </div>
  );
}
