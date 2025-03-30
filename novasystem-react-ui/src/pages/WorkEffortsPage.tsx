import React, { useState, useRef } from 'react';
import { useSystemStore } from '../store/systemStore';
import { Link } from 'react-router-dom'; // For linking to tasks
import { LuBriefcase } from 'react-icons/lu'; // Example icon

// --- Tooltip State Interface (copied) ---
interface TooltipState { /* ... */ }

function WorkEffortsPage() {
  // Get Data
  const systemStatus = useSystemStore((state: any) => state.systemStatus);
  const workEfforts = useSystemStore((state: any) => state.workEfforts);
  const workEffortIds = Object.keys(workEfforts);

  // --- Tooltip State ---
  const [tooltip, setTooltip] = useState<TooltipState>({ visible: false, message: '', top: 0, left: 0 });
  const tooltipTimeoutRef = useRef<number | null>(null);

  // --- State for expanded row ---
  const [expandedWorkEffortId, setExpandedWorkEffortId] = useState<string | null>(null);

  // --- Tooltip Helper ---
  const showClickTooltip = (event: React.MouseEvent<HTMLElement>, message: string) => {
     // ... existing helper code ...
  };

  // --- Handlers ---
  const handleCreateWorkEffort = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('[WorkEffortsPage] Create Work Effort clicked');
    showClickTooltip(e, 'Create Work Effort: Not Implemented');
  };

  // Renamed button handler to avoid conflict with row click
  const handleViewDetailsClick = (e: React.MouseEvent<HTMLButtonElement>, weId: string) => {
      e.stopPropagation(); // Prevent row click
      console.log(`[WorkEffortsPage] View Details ${weId} clicked`);
      showClickTooltip(e, 'View Details: Not Implemented');
  }

  // Work Effort Row Click Handler
  const handleWorkEffortRowClick = (weId: string) => {
      setExpandedWorkEffortId(current => current === weId ? null : weId);
  };

  return (
    <div>
      {/* ... Tooltip Element ... */}

      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Work Efforts</h1>
        <button className="button button-primary" onClick={handleCreateWorkEffort}>
          <LuBriefcase /> Create Work Effort
        </button>
      </div>

      {/* Work Efforts Table/List */}
      <div className="content-box">
         <div className="content-box-body no-padding">
             {systemStatus === 'connecting' ? (
                 <div className="loading-state">Loading work efforts...</div>
             ) : (
                 <table className="data-table">
                     <thead>
                         <tr>
                             <th>ID</th>
                             <th>Title</th>
                             <th>Status</th>
                             <th>Linked Tasks</th>
                             <th>Actions</th>
                         </tr>
                     </thead>
                     <tbody>
                         {workEffortIds.length > 0 ? (
                             workEffortIds.flatMap((weId) => { // Use flatMap
                                 const we = workEfforts[weId];
                                 const isExpanded = expandedWorkEffortId === weId;
                                 return [
                                     <tr key={weId} onClick={() => handleWorkEffortRowClick(weId)} className={isExpanded ? 'expanded-row-trigger' : ''} style={{ cursor: 'pointer' }}>
                                         <td>{we.id}</td>
                                         <td>{we.title}</td>
                                         <td>
                                             <span className={`pill status-${we.status}`}>
                                                {we.status}
                                             </span>
                                         </td>
                                         <td>
                                            {we.linkedTaskIds.length > 0 ? (
                                                 we.linkedTaskIds.map((taskId: string, index: number) => (
                                                    <React.Fragment key={taskId}>
                                                         <Link to="/tasks" state={{ filterTaskId: taskId }} className="inline-link">{taskId}</Link>
                                                         {index < we.linkedTaskIds.length - 1 ? ', ' : ''}
                                                     </React.Fragment>
                                                 ))
                                            ) : (
                                                 '-'
                                            )}
                                         </td>
                                         <td>
                                             {/* Updated button handler */}
                                             <button className="button button-secondary button-small" onClick={(e) => handleViewDetailsClick(e, weId)}>View</button>
                                         </td>
                                     </tr>,
                                     // --- Expanded Row ---
                                     isExpanded && (
                                         <tr key={`${weId}-details`} className="expanded-row-content">
                                             <td colSpan={5}> {/* Span all columns */}
                                                 <div className="details-content">
                                                     <h4>Details for Work Effort {we.id}</h4>
                                                     <p><strong>Title:</strong> {we.title}</p>
                                                     <p><strong>Status:</strong> {we.status}</p>
                                                     <p><strong>Linked Tasks:</strong></p>
                                                     {we.linkedTaskIds.length > 0 ? (
                                                        <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem' }}>
                                                             {we.linkedTaskIds.map((taskId: string) => (
                                                                <li key={taskId}>
                                                                    <Link to="/tasks" state={{ filterTaskId: taskId }} className="inline-link">{taskId}</Link>
                                                                </li>
                                                             ))}
                                                         </ul>
                                                     ) : (
                                                        <span style={{ fontStyle: 'italic', color: 'var(--text-color-secondary)' }}> None</span>
                                                     )}
                                                 </div>
                                             </td>
                                         </tr>
                                     )
                                 ];
                             })
                         ) : (
                             <tr>
                                 <td colSpan={5} className="empty-state">
                                     No work efforts found.
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

export default WorkEffortsPage;