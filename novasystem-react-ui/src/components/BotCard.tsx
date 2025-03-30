import React from 'react';
import { BotState } from '../store/systemStore'; // Import BotState type
import { LuBot } from 'react-icons/lu'; // Import Bot icon
import { Link } from 'react-router-dom'; // Import Link

interface BotCardProps {
    bot: BotState;
}

const BotCard: React.FC<BotCardProps> = ({ bot }) => {

    return (
        <Link
            to={`/bots/${bot.id}`} // Update link to dynamic route
            className="bot-card-link" // Add class for styling the link
        >
            <div className="bot-card">
                <div className="bot-card-header">
                    <div className="bot-card-info">
                        <LuBot className="card-icon"/>
                        <h4 title={bot.name}>{bot.name}</h4>
                    </div>
                     <span className={`status-dot status-${bot.status || 'idle'}`} title={`Status: ${bot.status}`}></span>
                </div>
                <p className="bot-id" title={bot.id}>ID: {bot.id}</p>
                {/* TODO: Add Task Input / Stream Output Area Here */}
                {/* TODO: Add actions like Pause/Resume Bot, View Details */}
            </div>
        </Link>
    );
};

export default BotCard;