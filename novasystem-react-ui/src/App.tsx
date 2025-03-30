import React, { useState, useRef } from 'react';
import { BrowserRouter, Routes, Route, Link, Outlet, useLocation } from 'react-router-dom';
import { useSystemStore } from './store/systemStore';
import HubCard from './components/HubCard';
import { LuServer, LuBot, LuActivity, LuTriangle } from 'react-icons/lu';
import DashboardPage from './pages/DashboardPage';
import HubsPage from './pages/HubsPage';
import BotsPage from './pages/BotsPage';
import TasksPage from './pages/TasksPage';
import WorkEffortsPage from './pages/WorkEffortsPage';
import './App.css';

interface TooltipState {
  visible: boolean;
  message: string;
  top: number;
  left: number;
}

// Component to render the navigation links and handle active state
const NavigationLinks = () => {
  const location = useLocation();
  const handleNavClick = (target: string) => console.log(`[App] Navigate to ${target} clicked (via Link)`);

  return (
    <div className="navbar-links">
      <Link to="/" className={location.pathname === '/' ? 'active' : ''} onClick={() => handleNavClick('Dashboard')}>Dashboard</Link>
      <Link to="/hubs" className={location.pathname === '/hubs' ? 'active' : ''} onClick={() => handleNavClick('Hubs')}>Hubs</Link>
      <Link to="/bots" className={location.pathname === '/bots' ? 'active' : ''} onClick={() => handleNavClick('Bots')}>Bots</Link>
      <Link to="/tasks" className={location.pathname === '/tasks' ? 'active' : ''} onClick={() => handleNavClick('Tasks')}>Tasks</Link>
      <Link to="/work-efforts" className={location.pathname === '/work-efforts' ? 'active' : ''} onClick={() => handleNavClick('Work Efforts')}>Work Efforts</Link>
    </div>
  );
};

function App() {
  // Get system status from store
  const systemStatus = useSystemStore((state: any) => state.systemStatus);

  // --- Local state/helpers for UI elements in App shell (like tooltip) ---
  const [tooltip, setTooltip] = useState<TooltipState>({ visible: false, message: '', top: 0, left: 0 });
  const tooltipTimeoutRef = useRef<number | null>(null);

  // Tooltip helper remains local to App shell
  const showClickTooltip = (event: React.MouseEvent<HTMLElement>, message: string) => {
    if (tooltipTimeoutRef.current !== null) { clearTimeout(tooltipTimeoutRef.current); tooltipTimeoutRef.current = null; }
    const rect = event.currentTarget.getBoundingClientRect();
    const tooltipTop = rect.top - rect.height - 10;
    const tooltipLeft = rect.left + rect.width / 2;
    setTooltip({ visible: true, message, top: tooltipTop + window.scrollY, left: tooltipLeft + window.scrollX });
    tooltipTimeoutRef.current = setTimeout(() => { setTooltip({ visible: false, message: '', top: 0, left: 0 }); tooltipTimeoutRef.current = null; }, 1500);
  };

  // Refresh handler remains local to App shell
  const handleRefresh = (e: React.MouseEvent<HTMLButtonElement>) => {
      console.log('[App] Refresh clicked');
      showClickTooltip(e, 'Refresh: Not Implemented');
  };
  // --- End Local state/helpers ---

  // Determine connection boolean from store status
  const isConnected = systemStatus === 'connected';

  // Removed other state getters (hubs, bots etc.) as they are not directly used in App shell

  return (
    <BrowserRouter>
      <div className="app-container">
        {/* Tooltip Element (uses local state) */}
        {tooltip.visible && (
          <div className="click-tooltip" style={{ top: `${tooltip.top}px`, left: `${tooltip.left}px`, transform: 'translateX(-50%)' }}>
            {tooltip.message}
          </div>
        )}

        <nav className="navbar">
          <div className="navbar-content">
            <div className="navbar-left">
              <div className="navbar-brand">
                <Link to="/" className="navbar-brand-link">
                  <span>NovaSystem</span>
                </Link>
              </div>
             <NavigationLinks /> {/* Use the new component */}
            </div>
            <div className="navbar-right">
              <span className="connection-status">
                 {/* Use isConnected derived from store status */}
                 <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
                {/* Display text based on store status */}
                {systemStatus === 'connected' ? 'Connected' : (systemStatus === 'connecting' ? 'Connecting...' : 'Disconnected')}
              </span>
               {/* Uses local handleRefresh */}
              <button className="button button-secondary" onClick={handleRefresh}>Refresh</button>
            </div>
          </div>
        </nav>

        {/* Page content rendered via Outlet */}
        <div className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/hubs" element={<HubsPage />} />
            <Route path="/bots" element={<BotsPage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/work-efforts" element={<WorkEffortsPage />} />
          </Routes>
         {/* Removed the potentially redundant Outlet here */}
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
