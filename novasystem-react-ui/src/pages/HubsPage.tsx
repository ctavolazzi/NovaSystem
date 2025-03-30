import React, { useState, useRef } from 'react';
import { useSystemStore } from '../store/systemStore';
import HubCard from '../components/HubCard';
import { LuServer } from 'react-icons/lu';

// --- Tooltip State Interface (copied) ---
interface TooltipState {
  visible: boolean;
  message: string;
  top: number;
  left: number;
}

function HubsPage() {
  // Get Hubs Data
  const systemStatus = useSystemStore((state: any) => state.systemStatus);
  const hubs = useSystemStore((state: any) => state.hubs);
  const hubIds = Object.keys(hubs);

  // --- Tooltip State (local to HubsPage) ---
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

  // Placeholder handler for adding a hub
  const handleAddHub = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('[HubsPage] Add Hub clicked');
    showClickTooltip(e, 'Add Hub: Not Implemented');
  };

  return (
    <div>
      {/* Tooltip Element */}
      {tooltip.visible && (
          <div className="click-tooltip" style={{ position:'absolute', top: `${tooltip.top}px`, left: `${tooltip.left}px`, transform: 'translateX(-50%)' }}>
            {tooltip.message}
          </div>
      )}

      {/* Use CSS class for header */}
      <div className="page-header">
        <h1 className="page-title">Hubs</h1>
        <button className="button button-primary" onClick={handleAddHub}>
          <LuServer /> Add Hub
        </button>
      </div>

      {/* Grid for Hub Cards / Loading / Empty State */}
      {systemStatus === 'connecting' ? (
          <div className="loading-state">Loading hubs...</div>
      ) : hubIds.length > 0 ? (
          <div className="hubs-grid">
            {hubIds.map((hubId) => (
              <HubCard key={hubId} hub={hubs[hubId]} />
            ))}
          </div>
      ) : (
          <div className="empty-state full-grid-span"> {/* Added class for spanning */}
             No hubs available
          </div>
      )}

    </div>
  );
}

export default HubsPage;