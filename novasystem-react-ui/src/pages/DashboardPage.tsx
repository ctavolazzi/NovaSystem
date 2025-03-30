import React, { useState, useRef } from 'react';
import { useSystemStore } from '../store/systemStore';
import HubCard from '../components/HubCard';
import { LuServer, LuBot, LuActivity, LuTriangle } from 'react-icons/lu';

function DashboardPage() {
  const systemStatus = useSystemStore((state: any) => state.systemStatus);
  const hubs = useSystemStore((state: any) => state.hubs);
  const bots = useSystemStore((state: any) => state.bots);
  const hubIds = Object.keys(hubs);
  const botIds = Object.keys(bots);

  const [expandedBotId, setExpandedBotId] = useState<string | null>(null);

  // --- Tooltip State & Helper (Needed locally for Start/Stop) ---
  const [tooltip, setTooltip] = useState<TooltipState>({ visible: false, message: '', top: 0, left: 0 });
  const tooltipTimeoutRef = useRef<number | null>(null);
  const showClickTooltip = (event: React.MouseEvent<HTMLElement>, message: string) => {
    if (tooltipTimeoutRef.current !== null) { clearTimeout(tooltipTimeoutRef.current); tooltipTimeoutRef.current = null; }
    const rect = event.currentTarget.getBoundingClientRect();
    const tooltipTop = rect.top - rect.height - 10;
    const tooltipLeft = rect.left + rect.width / 2;
    setTooltip({ visible: true, message, top: tooltipTop + window.scrollY, left: tooltipLeft + window.scrollX });
    tooltipTimeoutRef.current = setTimeout(() => { setTooltip({ visible: false, message: '', top: 0, left: 0 }); tooltipTimeoutRef.current = null; }, 1500);
  };
  // --- End Tooltip Logic ---

  const handleBotRowClick = (botId: string) => {
    setExpandedBotId(currentExpandedId =>
      currentExpandedId === botId ? null : botId
    );
  };

  const totalHubs = hubIds.length;
  const totalBots = botIds.length;

  // Updated Bot Action Handlers
  const handleStartBot = (e: React.MouseEvent<HTMLButtonElement>, botId: string) => {
      e.stopPropagation();
      console.log(`[DashboardPage] Start Bot ${botId} clicked`);
      showClickTooltip(e, 'Start Bot: Not Implemented'); // Use tooltip
  };
  const handleStopBot = (e: React.MouseEvent<HTMLButtonElement>, botId: string) => {
      e.stopPropagation();
      console.log(`[DashboardPage] Stop Bot ${botId} clicked`);
      showClickTooltip(e, 'Stop Bot: Not Implemented'); // Use tooltip
  };

  return (
    <>
      {/* --- Tooltip Element --- */}
      {tooltip.visible && (
          <div className="click-tooltip" style={{ position:'absolute', top: `${tooltip.top}px`, left: `${tooltip.left}px`, transform: 'translateX(-50%)' }}>
            {tooltip.message}
          </div>
      )}

      <h1 className="page-title">Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-header">
            <LuServer className="stat-icon" />
            <span>Hubs</span>
          </div>
          <p className="stat-value">{totalHubs}</p>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <LuBot className="stat-icon" />
            <span>Bots</span>
          </div>
          <p className="stat-value">{totalBots}</p>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <LuActivity className="stat-icon" />
            <span>Active Tasks</span>
          </div>
          <p className="stat-value">0</p>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <LuTriangle className="stat-icon error" />
            <span>Errors</span>
          </div>
          <p className="stat-value">0</p>
        </div>
      </div>

      <div className="main-content-grid">
        <div className="main-column">
          <div className="content-box hubs-overview">
            <div className="content-box-header">
              <h2>Hubs Overview</h2>
            </div>
            <div className="content-box-body">
              <div className="hubs-grid">
                {hubIds.length > 0 ? (
                  hubIds.map((hubId) => (
                    <HubCard key={hubId} hub={hubs[hubId]} />
                  ))
                ) : (
                  <div className="empty-state">
                    {systemStatus === 'connecting' ? 'Connecting to backend...' : 'No hubs available'}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="content-box bot-management">
            <div className="content-box-header">
              <h2>Bot Management</h2>
              <span className="pill">{totalBots} bots</span>
            </div>
            <div className="content-box-body no-padding">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Bot ID</th>
                    <th>Status</th>
                    <th>Hub</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {botIds.length > 0 ? (
                    botIds.flatMap((botId) => {
                      const bot = bots[botId];
                      const isExpanded = expandedBotId === botId;
                      return [
                        <tr key={botId} onClick={() => handleBotRowClick(botId)} className={isExpanded ? 'expanded-row-trigger' : ''} style={{ cursor: 'pointer' }}>
                          <td>{bot.name || botId}</td>
                          <td>
                            <span className={`pill status-${bot.status || 'idle'}`}>
                              {bot.status || 'idle'}
                            </span>
                          </td>
                          <td>{bot.hubId}</td>
                          <td>
                            <button className="button button-primary button-small" onClick={(e) => handleStartBot(e, botId)}>Start</button>
                            <button className="button button-secondary button-small" onClick={(e) => handleStopBot(e, botId)}>Stop</button>
                          </td>
                        </tr>,
                        isExpanded && (
                           <tr key={`${botId}-details`} className="expanded-row-content">
                              <td colSpan={4}>
                                <div style={{ padding: '1rem' }}>
                                  <h4>Details for {bot.name || botId}</h4>
                                  <p>Journal:</p>
                                  <pre>
                                    Log entry 1...
                                    Log entry 2...
                                  </pre>
                                  <p>Logs:</p>
                                  <pre>
                                    Debug message...
                                    Info message...
                                  </pre>
                                </div>
                              </td>
                            </tr>
                        )
                      ];
                    })
                  ) : (
                     <tr>
                        <td colSpan={4} className="empty-state">
                          No bots available
                        </td>
                      </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="side-column">
          <div className="content-box recent-events">
            <div className="content-box-header">
              <h2>Recent Events</h2>
            </div>
            <div className="content-box-body">
                <div className="event-item">
                  <span className="event-indicator connected">●</span> System connected
                </div>
                <div className="event-item">
                  <span className="event-indicator idle">●</span> Alpha Hub idle
                </div>
                <div className="event-item">
                  <span className="event-indicator info">●</span> Bot added to hub
                </div>
              </div>
          </div>
        </div>
      </div>
    </>
  );
}

// Need TooltipState interface here too
interface TooltipState {
  visible: boolean;
  message: string;
  top: number;
  left: number;
}

export default DashboardPage;