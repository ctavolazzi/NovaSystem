import React, { useState, useRef } from 'react';
import { HubState, BotState } from '../store/systemStore'; // Import needed types
import BotCard from './BotCard';
import { useSystemStore } from '../store/systemStore';
import { LuServer, LuBot, LuPlus } from 'react-icons/lu'; // Import Hub/Bot icons

interface HubCardProps {
    hub: HubState;
}

// --- Tooltip State Interface (copied) ---
interface TooltipState {
  visible: boolean;
  message: string;
  top: number;
  left: number;
}

const HubCard: React.FC<HubCardProps> = ({ hub }) => {
    // Get all bots from the store to filter by ID
    const bots = useSystemStore((state) => state.bots);
    const hubBots: BotState[] = hub.botIds
        .map((botId: string) => bots[botId]) // Type botId
        .filter((bot): bot is BotState => bot !== undefined); // Type guard filter

    // --- Tooltip State (local to HubCard) ---
    const [tooltip, setTooltip] = useState<TooltipState>({ visible: false, message: '', top: 0, left: 0 });
    const tooltipTimeoutRef = useRef<number | null>(null); // Ref for timeout ID (number type)

    // --- Helper for Click Tooltip Feedback (copied) ---
    const showClickTooltip = (event: React.MouseEvent<HTMLElement>, message: string) => {
      if (tooltipTimeoutRef.current !== null) {
        clearTimeout(tooltipTimeoutRef.current);
        tooltipTimeoutRef.current = null;
      }
      const rect = event.currentTarget.getBoundingClientRect();
      const tooltipTop = rect.top - rect.height - 10;
      const tooltipLeft = rect.left + rect.width / 2;
      setTooltip({
        visible: true,
        message,
        top: tooltipTop + window.scrollY,
        left: tooltipLeft + window.scrollX
      });
      tooltipTimeoutRef.current = setTimeout(() => {
        setTooltip({ visible: false, message: '', top: 0, left: 0 });
        tooltipTimeoutRef.current = null;
      }, 1500);
    };

    const handleAddBotToHub = (e: React.MouseEvent<HTMLButtonElement>, hubId: string) => {
        console.log(`[HubCard] Add Bot to Hub ${hubId} clicked`);
        showClickTooltip(e, 'Add Bot: Not Implemented'); // Use tooltip helper
    }

    return (
        // Slightly lighter bg, softer shadow
        <div className="hub-card">
            {/* --- Tooltip Element (local to HubCard) --- */}
            {tooltip.visible && (
                <div
                className="click-tooltip"
                style={{
                    position: 'absolute', // Needs position absolute
                    top: `${tooltip.top}px`,
                    left: `${tooltip.left}px`,
                    transform: 'translateX(-50%)',
                }}
                >
                {tooltip.message}
                </div>
            )}

            {/* Card Header */}
            <div className="card-header">
                <LuServer className="card-icon" />
                <div className="card-header-text">
                    <h3 title={hub.name}>{hub.name}</h3>
                    <p title={hub.id}>ID: {hub.id}</p>
                </div>
                 <span className="pill">{hubBots.length} Bot(s)</span>
            </div>

            {/* Card Body - Bots List */}
            <div className="card-body" style={{maxHeight: '300px'}}> {/* Limit height & scroll bots if too many */}
                {hubBots.length > 0 ? (
                    hubBots.map((bot) => (
                        <BotCard key={bot.id} bot={bot} />
                    ))
                ) : (
                    <p className="empty-state">No bots in this hub.</p>
                )}
            </div>

             {/* Card Footer - Actions */}
             <div className="card-footer">
                 <button className="button button-primary button-small button-full" onClick={(e) => handleAddBotToHub(e, hub.id)}>
                      <LuPlus size={14} /> Add Bot
                 </button>
             </div>
        </div>
    );
};

export default HubCard;