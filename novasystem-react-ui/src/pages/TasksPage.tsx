import React, { useState, useRef } from 'react';
import { useSystemStore } from '../store/systemStore'; // Import store
import { TaskState } from '../store/systemStore'; // Import TaskState type
import { LuActivity } from 'react-icons/lu'; // Example icon
import { Link } from 'react-router-dom';

// --- Tooltip State Interface (copied) ---
interface TooltipState {
  visible: boolean;
  message: string;
  top: number;
  left: number;
}

// Helper function to format date strings nicely
const formatDate = (isoString: string | null) => {
  if (!isoString) return '-';
  try {
    return new Date(isoString).toLocaleString();
  } catch (e) {
    return 'Invalid Date';
  }
};

function TasksPage() {
  // Get Task Data
  const systemStatus = useSystemStore((state: any) => state.systemStatus);
  const tasks = useSystemStore((state: any) => state.tasks);
  const taskIds = Object.keys(tasks);

  // --- Tooltip State (local to TasksPage) ---
  const [tooltip, setTooltip] = useState<TooltipState>({ visible: false, message: '', top: 0, left: 0 });
  const tooltipTimeoutRef = useRef<number | null>(null);

  // --- State for expanded row ---
  const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null);

  // --- Helper for Click Tooltip Feedback (copied) ---
  const showClickTooltip = (event: React.MouseEvent<HTMLElement>, message: string) => {
    if (tooltipTimeoutRef.current !== null) { clearTimeout(tooltipTimeoutRef.current); tooltipTimeoutRef.current = null; }
    const rect = event.currentTarget.getBoundingClientRect();
    const tooltipTop = rect.top - rect.height - 10;
    const tooltipLeft = rect.left + rect.width / 2;
    setTooltip({ visible: true, message, top: tooltipTop + window.scrollY, left: tooltipLeft + window.scrollX });
    tooltipTimeoutRef.current = setTimeout(() => { setTooltip({ visible: false, message: '', top: 0, left: 0 }); tooltipTimeoutRef.current = null; }, 1500);
  };

  // --- Placeholder Handlers ---
  const handleCreateTask = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('[TasksPage] Create Task clicked');
    showClickTooltip(e, 'Create Task: Not Implemented');
  };
  // Add handlers for task actions (view details, retry, cancel?) later
  const handleTaskAction = (e: React.MouseEvent<HTMLButtonElement>, taskId: string, action: string) => {
      e.stopPropagation(); // Prevent potential parent clicks
      console.log(`[TasksPage] Task ${taskId} Action: ${action}`);
      showClickTooltip(e, `${action}: Not Implemented`);
  }

  // Task Row Click Handler
  const handleTaskRowClick = (taskId: string) => {
      setExpandedTaskId(current => current === taskId ? null : taskId);
  };

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
            <h1 className="page-title">Tasks</h1>
            {/* Example Button */}
            <button className="button button-primary" onClick={handleCreateTask}>
                Create Task
            </button>
        </div>

        {/* Task Table Content Box */}
        <div className="content-box">
            <div className="content-box-header">
                <h2>Task Overview</h2>
                <span className="pill">{taskIds.length} tasks</span>
            </div>
             <div className="content-box-body no-padding">
                {systemStatus === 'connecting' ? (
                    <div className="loading-state">Loading tasks...</div>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Description</th>
                                <th>Status</th>
                                <th>Assigned Bot</th>
                                <th>Created At</th>
                                <th>Result/Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {taskIds.length > 0 ? (
                                taskIds.flatMap((taskId) => {
                                    const task = tasks[taskId];
                                    const isExpanded = expandedTaskId === taskId;
                                    return [
                                        <tr key={taskId} onClick={() => handleTaskRowClick(taskId)} className={isExpanded ? 'expanded-row-trigger' : ''} style={{ cursor: 'pointer' }}>
                                            <td>{task.id}</td>
                                            <td>{task.description}</td>
                                            <td>
                                                <span className={`pill status-${task.status}`}>
                                                    {task.status}
                                                </span>
                                            </td>
                                            <td>{task.assignedBotId || '-'}</td>
                                            <td>{formatDate(task.createdAt)}</td>
                                            <td>
                                                {task.status === 'completed' || task.status === 'failed' ? (
                                                    <span title={task.result || ''} style={{fontSize: '0.8rem', color: 'var(--text-color-secondary)'}}>
                                                        {(task.result || '-').substring(0, 30)}{task.result && task.result.length > 30 ? '...' : ''}
                                                    </span>
                                                ) : (
                                                   <button
                                                        className="button button-secondary button-small"
                                                        onClick={(e) => handleTaskAction(e, taskId, 'Cancel')}
                                                    >
                                                        Cancel
                                                    </button>
                                                )}
                                                {/* Add more actions like Retry for failed tasks? */}
                                            </td>
                                        </tr>,
                                        isExpanded && (
                                            <tr key={`${taskId}-details`} className="expanded-row-content">
                                                <td colSpan={6}>
                                                    <div className="details-content">
                                                        <h4>Details for Task {task.id}</h4>
                                                        <p><strong>Description:</strong> {task.description}</p>
                                                        <p><strong>Status:</strong> {task.status}</p>
                                                        <p><strong>Created:</strong> {formatDate(task.createdAt)}</p>
                                                        <p><strong>Completed:</strong> {formatDate(task.completedAt)}</p>
                                                        <p><strong>Assigned Bot:</strong> {task.assignedBotId || 'None'}</p>
                                                        <p><strong>Result:</strong></p>
                                                        <pre style={{ whiteSpace: 'pre-wrap' }}>{task.result || 'N/A'}</pre>
                                                        <p><strong>Related Work Effort:</strong>
                                                            {task.relatedWorkEffortId ? (
                                                                <Link
                                                                    to="/work-efforts"
                                                                    state={{ filterWorkEffortId: task.relatedWorkEffortId }}
                                                                    className="inline-link"
                                                                >
                                                                    {task.relatedWorkEffortId}
                                                                </Link>
                                                            ) : (
                                                                'None'
                                                            )}
                                                        </p>
                                                    </div>
                                                </td>
                                            </tr>
                                        )
                                    ];
                                })
                            ) : (
                                <tr>
                                    <td colSpan={6} className="empty-state">
                                        No tasks available
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

export default TasksPage;