import React, { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useSystemStore, SystemState, BotState } from '../store/systemStore';

// Define the expected shape of the system state data from the backend
// Re-using interfaces from store might be better if they perfectly match
interface BackendSystemState {
    systemStatus: string;
    hubs: Record<string, any>; // Use more specific types if possible
    bots: Record<string, any>;
}

// Make sure this matches the backend URL and port
const SOCKET_SERVER_URL = 'ws://localhost:5002'; // Use ws:// or wss://

export const useWebSocket = () => {
    const socketRef = useRef<Socket | null>(null);
    const setStoreStatus = useSystemStore((state) => state.setSystemStatus);
    const [lastError, setLastError] = useState<string | null>(null);

    useEffect(() => {
        if (socketRef.current) return;

        console.log('Attempting to connect to WebSocket...');
        setStoreStatus('connecting');
        const socket = io(SOCKET_SERVER_URL, {
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            transports: ['websocket'], // Prefer websockets
        });
        socketRef.current = socket;

        socket.on('connect', () => {
            console.log('WebSocket connected:', socket.id);
            setLastError(null);
            socket.emit('request_initial_state');
        });

        socket.on('disconnect', (reason) => {
            console.warn('WebSocket disconnected:', reason);
            setStoreStatus('disconnected');
            if (reason === 'io server disconnect') {
                socket.connect(); // Optional: attempt immediate reconnect
            }
        });

        socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            setStoreStatus('disconnected');
            setLastError(`Connection Error: ${error.message}`);
        });

        socket.on('system_state', (data: BackendSystemState) => {
            console.log('Received system_state:', data);
            useSystemStore.setState({
                systemStatus: data.systemStatus as SystemState['systemStatus'],
                hubs: data.hubs,
                bots: data.bots,
            });
        });

        socket.on('bot_status_update', (data: { botId: string; status: BotState['status'] }) => {
            console.log('Received bot_status_update:', data);
            useSystemStore.getState().updateBotStatus(data.botId, data.status);
        });

        return () => {
            console.log('Disconnecting WebSocket...');
            socket.disconnect();
            socketRef.current = null;
            setStoreStatus('disconnected');
        };
    }, [setStoreStatus]);

    return { lastError };
};