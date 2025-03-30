import React from 'react';
import { useSystemStore } from '../store/systemStore';
import { LuActivity, LuPlugZap, LuUnplug, LuCirclePlus, LuLayoutDashboard } from "react-icons/lu";

interface SidebarProps {
    isConnected: boolean;
    lastError: string | null;
    // TODO: Add props for actions like onAddHubClick
}

const Sidebar: React.FC<SidebarProps> = ({ isConnected, lastError }) => {
    const systemStatus = useSystemStore((state) => state.systemStatus);

    return (
        <aside className="w-64 bg-gradient-to-b from-slate-800 to-slate-900 p-4 flex flex-col border-r border-slate-700 text-slate-300 flex-shrink-0">
            <div className="flex items-center gap-2 mb-6">
                 <LuLayoutDashboard className="text-sky-400 w-6 h-6" />
                 <h2 className="text-xl font-semibold text-sky-400">System Control</h2>
             </div>

            {/* Connection Status */}
            <div className="mb-4 p-3 bg-slate-700/50 rounded-lg border border-slate-600/50">
                <h3 className="text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider flex items-center gap-1.5">
                    {isConnected ? <LuPlugZap className="text-green-400"/> : <LuUnplug className="text-red-400"/>}
                    Connection
                </h3>
                <div className={`text-sm font-medium ${isConnected ? 'text-green-300' : 'text-red-300'}`}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                </div>
                {lastError && <p className="text-xs text-red-400 mt-1">{lastError}</p>}
            </div>

             {/* System Status */}
             <div className="mb-4 p-3 bg-slate-700/50 rounded-lg border border-slate-600/50">
                <h3 className="text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider flex items-center gap-1.5">
                    <LuActivity />
                    Status
                </h3>
                 <p className="text-lg font-semibold text-slate-100 capitalize">{systemStatus}</p>
            </div>

            {/* Global Actions */}
            <div className="mt-auto pt-4 border-t border-slate-700">
                 <h3 className="text-sm font-medium text-slate-400 mb-2">Actions</h3>
                <button
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    // onClick={onAddHubClick} // TODO: Implement later
                    disabled={!isConnected} // Example: Disable if not connected
                    title={!isConnected ? "Connect to backend to add hubs" : "Add a new Hub"}
                >
                     <LuCirclePlus /> Add Hub
                </button>
                {/* TODO: Add Pause/Resume buttons here */}
            </div>

        </aside>
    );
};

export default Sidebar;