import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Analyze from './pages/Analyze';
import Violations from './pages/Violations';
import Challans from './pages/Challans';
import './index.css';

export default function App() {
  const [page, setPage] = useState('dashboard');

  const renderPage = () => {
    switch (page) {
      case 'dashboard':  return <Dashboard />;
      case 'analyze':    return <Analyze />;
      case 'violations': return <Violations />;
      case 'challans':   return <Challans />;
      default:           return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Sidebar active={page} onNav={setPage} />
      <main className="main">
        {renderPage()}
      </main>
    </div>
  );
}
