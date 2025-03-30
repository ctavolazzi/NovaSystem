import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useSystemStore, JournalEntry } from '../store/systemStore';
import { LuArrowLeft } from 'react-icons/lu';

// Helper function to format date strings nicely (copied from TasksPage)
const formatDate = (isoString: string | null) => {
  if (!isoString) return '-';
  try {
    return new Date(isoString).toLocaleString();
  } catch (e) {
    return 'Invalid Date';
  }
};

function BotDetailPage() {
  const { botId } = useParams<{ botId: string }>(); // Get botId from URL
  const bot = useSystemStore((state: any) => state.bots[botId || '']);

  if (!botId || !bot) {
    return (
      <div>
        <Link to="/bots" className="inline-link mb-4 block"> <LuArrowLeft className="inline mr-1"/> Back to Bots</Link>
        <h1 className="page-title">Bot Not Found</h1>
        <p>Could not find details for Bot ID: {botId}</p>
      </div>
    );
  }

  return (
    <div>
        <Link to="/bots" className="inline-link mb-4 block"> <LuArrowLeft className="inline mr-1"/> Back to Bots</Link>
        <div className="page-header">
             <h1 className="page-title">Bot: {bot.name} ({bot.id})</h1>
             {/* Add relevant actions here later? Like start/stop specific to this bot */}
        </div>

        <div className="content-box">
            <div className="content-box-body">
                {/* Display Bot Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div><strong>Status:</strong> <span className={`pill status-${bot.status}`}>{bot.status}</span></div>
                    <div><strong>Hub ID:</strong> <Link to="/hubs" state={{ highlightHubId: bot.hubId}} className="inline-link">{bot.hubId}</Link></div>
                </div>

                {/* Display Journal */}
                <h4>Journal</h4>
                <div className="journal-entries">
                    {bot.journal && bot.journal.length > 0 ? (
                        bot.journal.map((entry: JournalEntry, index: number) => (
                            <div key={index} className="journal-entry">
                                <span className="journal-timestamp">{formatDate(entry.timestamp)}</span>
                                <span className={`journal-type type-${entry.type.toLowerCase()}`}>{entry.type}</span>
                                <span className="journal-summary">{entry.summary}</span>
                                {entry.details && (
                                    <pre className="journal-details">
                                        {typeof entry.details === 'string'
                                            ? entry.details
                                            : JSON.stringify(entry.details, null, 2)}
                                    </pre>
                                )}
                            </div>
                        ))
                    ) : (
                        <p className="empty-state-text">No journal entries.</p>
                    )}
                </div>

                {/* Display Logs */}
                <h4 style={{marginTop: '1.5rem'}}>Logs</h4>
                <pre className="detail-pre">
                    {/* Logs are still string[] */}
                    {bot.logs && bot.logs.length > 0
                        ? bot.logs.join('\n')
                        : 'No log entries.'}
                </pre>

                 {/* Add Task History Section? */}
            </div>
        </div>
    </div>
  );
}

export default BotDetailPage;