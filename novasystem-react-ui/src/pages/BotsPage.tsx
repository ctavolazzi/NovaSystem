import React, { useState, useRef } from 'react';
import { useSystemStore } from '../store/systemStore';
import { LuBot } from 'react-icons/lu';

// --- Tooltip State Interface (copied) ---
interface TooltipState {
  visible: boolean;
  message: string;
  top: number;
  left: number;
}

function BotsPage() {
  // Get Bot Data
  const systemStatus = useSystemStore((state: any) => state.systemStatus);
  const bots = useSystemStore((state: any) => state.bots);
  const botIds = Object.keys(bots);

  // State for expanded row (copied from DashboardPage)
  const [expandedBotId, setExpandedBotId] = useState<string | null>(null);

  // --- Tooltip State (local to BotsPage) ---
  const [tooltip, setTooltip] = useState<TooltipState>({ visible: false, message: '', top: 0, left: 0 });
  const tooltipTimeoutRef = useRef<number | null>(null);

  // --- Helper for Click Tooltip Feedback (copied) ---
  const showClickTooltip = (event: React.MouseEvent<HTMLElement>, message: string) => {
    if (tooltipTimeoutRef.current !== null) { clearTimeout(tooltipTimeoutRef.current); tooltipTimeoutRef.current = null; }
    const rect = event.currentTarget.getBoundingClientRect();
    const tooltipTop = rect.top - rect.height - 10;
    const tooltipLeft = rect.left + rect.width / 2;
    setTooltip({ visible: true, message, top: tooltipTop + window.scrollY, left: tooltipLeft + window.scrollX });
    tooltipTimeoutRef.current = setTimeout(() => { setTooltip({ visible: false, message: '', top: 0, left: 0 }); tooltipTimeoutRef.current = null; }, 1500);
  };

  // --- Handlers ---
  const handleDeployBot = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('[BotsPage] Deploy Bot clicked');
    showClickTooltip(e, 'Deploy Bot: Not Implemented');
  };

  const handleBotRowClick = (botId: string) => {
    setExpandedBotId(currentExpandedId =>
      currentExpandedId === botId ? null : botId
    );
    // No fetch simulation needed now
  };

  const handleStartBot = (e: React.MouseEvent<HTMLButtonElement>, botId: string) => {
      e.stopPropagation();
      console.log(`[BotsPage] Start Bot ${botId} clicked - Not Implemented`);
      showClickTooltip(e, 'Start Bot: Not Implemented');
  };
  const handleStopBot = (e: React.MouseEvent<HTMLButtonElement>, botId: string) => {
      e.stopPropagation();
      console.log(`[BotsPage] Stop Bot ${botId} clicked - Not Implemented`);
      showClickTooltip(e, 'Stop Bot: Not Implemented');
  };
  // --- End Handlers ---

  return (
    <div>
      {/* Tooltip Element */}
      {tooltip.visible && (
          <div className="click-tooltip" style={{ position:'absolute', top: `${tooltip.top}px`, left: `${tooltip.left}px`, transform: 'translateX(-50%)' }}>
            {tooltip.message}
          </div>
      )}

      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Bots</h1>
        <button className="button button-secondary" onClick={handleDeployBot}> {/* Using secondary style here */}
          <LuBot /> Deploy Bot
        </button>
      </div>

      {/* Bot Table Content Box */}
      <div className="content-box">
        <div className="content-box-header">
            <h2>Bot Management</h2>
            <span className="pill">{botIds.length} bots</span>
        </div>
        <div className="content-box-body no-padding">
          {systemStatus === 'connecting' ? (
             <div className="loading-state">Loading bots...</div>
          ) : (
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
                                <div className="details-content">
                                  <h4>Details for {bot.name || botId}</h4>
                                  <p>Journal:</p>
                                  <pre>
                                    {bot.journal && bot.journal.length > 0
                                      ? bot.journal.join('\n')
                                      : 'No journal entries.'}
                                  </pre>
                                  <p>Logs:</p>
                                  <pre>
                                    {bot.logs && bot.logs.length > 0
                                      ? bot.logs.join('\n')
                                      : 'No log entries.'}
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
          )}
        </div>
      </div>

    </div>
  );
}

export default BotsPage;