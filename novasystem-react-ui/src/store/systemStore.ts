import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid'; // Import uuid

// --- New Journal Entry Interface ---
export interface JournalEntry {
  timestamp: string;
  type: 'Action' | 'Observation' | 'Decision' | 'Error' | 'Info';
  summary: string;
  details?: Record<string, any> | string;
}

// Interface for Hub state
export interface HubState {
  id: string;
  name: string;
  botIds: string[];
}

// Interface for Bot state
export interface BotState {
  id: string;
  hubId: string;
  name: string;
  status: 'idle' | 'running' | 'error';
  journal: JournalEntry[]; // Use the new interface
  logs: string[];    // Added
  currentTaskDescription: string | null; // Added
  lastActivityTimestamp: string | null;   // Added
}

// Interface for Task state
export interface TaskState {
    id: string;
    description: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    assignedBotId: string | null;
    createdAt: string;
    completedAt: string | null;
    result: string | null;
    relatedWorkEffortId: string | null;
}

// --- Added Work Effort State Interface ---
export interface WorkEffortState {
    id: string;
    title: string;
    status: 'active' | 'completed' | 'planned';
    linkedTaskIds: string[];
    // description?: string; // Optional fields
}

// Interface for the entire system state
export interface SystemState {
  systemStatus: 'connecting' | 'connected' | 'disconnected';
  hubs: Record<string, HubState>;
  bots: Record<string, BotState>;
  tasks: Record<string, TaskState>;
  workEfforts: Record<string, WorkEffortState>; // Added
  // Actions
  setSystemStatus: (status: 'connecting' | 'connected' | 'disconnected') => void;
  addHub: (hub: HubState) => void;
  addBot: (bot: BotState) => void;
  updateBotStatus: (botId: string, status: 'idle' | 'running' | 'error') => void;
  // Internal action for fetching mock data
  _fetchInitialData: () => void;
}

// --- Generate some UUIDs for mock data ---
const mockHubId1 = uuidv4();
const mockHubId2 = uuidv4();
const mockBotIdA = uuidv4();
const mockBotIdB = uuidv4();
const mockTaskId1 = uuidv4();
const mockTaskId2 = uuidv4();
const mockTaskId3 = uuidv4();
const mockWorkEffortId1 = `WE-${uuidv4().substring(0, 8).toUpperCase()}`;
const mockWorkEffortId2 = `WE-${uuidv4().substring(0, 8).toUpperCase()}`;
const mockWorkEffortId3 = `WE-${uuidv4().substring(0, 8).toUpperCase()}`;

// Mock Data with UUIDs and improved journal format
const mockHubs: Record<string, HubState> = {
  [mockHubId1]: {
    id: mockHubId1,
    name: 'Alpha Hub',
    botIds: [mockBotIdA, mockBotIdB]
  },
  [mockHubId2]: {
      id: mockHubId2,
      name: 'Beta Hub',
      botIds: []
  }
};

const mockBots: Record<string, BotState> = {
  [mockBotIdA]: {
    id: mockBotIdA,
    hubId: mockHubId1,
    name: `Bot ${mockBotIdA.substring(0, 6)}`,
    status: 'idle',
    journal: [
        {
            timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
            type: 'Info',
            summary: 'Bot instance created',
            details: { assignedHub: mockHubId1 }
        },
        {
            timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
            type: 'Decision',
            summary: 'Assigned Task',
            details: { taskId: mockTaskId1, reason: 'Available, matching capabilities' }
        },
        {
            timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
            type: 'Action',
            summary: 'Task Completed',
            details: `Task ${mockTaskId1}. Result: Successfully processed 105 records.`
        },
        {
            timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
            type: 'Decision',
            summary: 'Assigned Task',
            details: { taskId: mockTaskId2, reason: 'Available' }
        },
        {
            timestamp: new Date(Date.now() - 1000 * 60 * 1).toISOString(),
            type: 'Error',
            summary: 'Task Failed',
            details: `Task ${mockTaskId2}. Result: Error: Simulation diverged at step 5.`
        },
        {
            timestamp: new Date().toISOString(),
            type: 'Info',
            summary: 'Awaiting task assignment'
        }
    ], // Array of objects
    logs: [
        `[INFO] ${new Date().toISOString()} - Configuration loaded.`,
        `[DEBUG] ${new Date().toISOString()} - Pinging hub ${mockHubId1}...`,
        `[INFO] ${new Date().toISOString()} - Hub connection successful.`,
        `[INFO] ${new Date().toISOString()} - Diagnostics OK.`
    ],
    currentTaskDescription: null, // Idle, so no current task description
    lastActivityTimestamp: new Date().toISOString() // Last activity is now (idle)
  },
  [mockBotIdB]: {
    id: mockBotIdB,
    hubId: mockHubId1,
    name: `Bot ${mockBotIdB.substring(0, 6)}`,
    status: 'running', // Let's make this one seem busy
    journal: [
         {
            timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
            type: 'Info',
            summary: 'Bot instance created',
            details: { assignedHub: mockHubId1 }
        },
        {
            timestamp: new Date().toISOString(),
            type: 'Info',
            summary: 'Idle. Awaiting assignment.'
        }
    ], // Array of objects
    logs: [
        `[INFO] ${new Date(Date.now() - 1000 * 60 * 10).toISOString()} - Bot online.`,
        `[INFO] ${new Date(Date.now() - 1000 * 5).toISOString()} - Starting task: Analyze sensor data feed.` // Add a recent log
    ],
    currentTaskDescription: 'Analyzing sensor data feed (Batch 7/10)', // Example active task
    lastActivityTimestamp: new Date(Date.now() - 1000 * 5).toISOString() // Corresponds to last log entry
  }
};

const mockTasks: Record<string, TaskState> = {
    [mockTaskId1]: {
        id: mockTaskId1,
        description: 'Process data file input.csv',
        status: 'completed',
        assignedBotId: mockBotIdA,
        createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        completedAt: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
        result: 'Successfully processed 105 records.',
        relatedWorkEffortId: mockWorkEffortId1
    },
    [mockTaskId2]: {
        id: mockTaskId2,
        description: 'Run simulation model X',
        status: 'failed',
        assignedBotId: mockBotIdA,
        createdAt: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
        completedAt: new Date(Date.now() - 1000 * 60 * 7).toISOString(),
        result: 'Error: Simulation diverged at step 5.',
        relatedWorkEffortId: mockWorkEffortId1
    },
    [mockTaskId3]: {
        id: mockTaskId3,
        description: 'Monitor network traffic on subnet Y',
        status: 'pending',
        assignedBotId: null,
        createdAt: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
        completedAt: null,
        result: null,
        relatedWorkEffortId: mockWorkEffortId2
    },
};

const mockWorkEfforts: Record<string, WorkEffortState> = {
    [mockWorkEffortId1]: {
        id: mockWorkEffortId1,
        title: 'Process Initial Dataset',
        status: 'active',
        linkedTaskIds: [mockTaskId1, mockTaskId2]
    },
    [mockWorkEffortId2]: {
        id: mockWorkEffortId2,
        title: 'Set up Network Monitoring',
        status: 'planned',
        linkedTaskIds: [mockTaskId3]
    },
    [mockWorkEffortId3]: {
        id: mockWorkEffortId3,
        title: 'Infrastructure Upgrade',
        status: 'completed',
        linkedTaskIds: []
    }
};

// Create the Zustand store
export const useSystemStore = create<SystemState>((set) => ({
  systemStatus: 'connecting',
  hubs: {},
  bots: {},
  tasks: {},
  workEfforts: {}, // Added

  setSystemStatus: (status) => set({ systemStatus: status }),

  addHub: (hub) => set((state) => ({ hubs: { ...state.hubs, [hub.id]: hub } })),

  addBot: (bot) => set((state) => ({ bots: { ...state.bots, [bot.id]: bot } })),

  updateBotStatus: (botId, status) => set((state) => ({
    bots: {
      ...state.bots,
      [botId]: { ...state.bots[botId], status: status }
    }
  })),

  _fetchInitialData: () => {
    console.log('[Store] Simulating initial data fetch (UUIDs & improved mocks)...');
    setTimeout(() => {
        set({
            hubs: mockHubs,
            bots: mockBots,
            tasks: mockTasks,
            workEfforts: mockWorkEfforts,
            systemStatus: 'connected'
        });
        console.log('[Store] Mock data loaded and status set to connected.');
    }, 1500);
  }
}));

// Trigger fetch
useSystemStore.getState()._fetchInitialData();