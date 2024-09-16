import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

async function initializeDatabase() {
    const db = await open({
        filename: 'game.db',
        driver: sqlite3.Database
    });
    
    await db.exec(`
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            character_class TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS game_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            current_scene TEXT NOT NULL,
            character_state TEXT NOT NULL,
            inventory TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES game_sessions(id)
        );
        
        CREATE TABLE IF NOT EXISTS action_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            action TEXT NOT NULL,
            result TEXT NOT NULL,
            state_changes TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES game_sessions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_game_states_session_id ON game_states(session_id);
        CREATE INDEX IF NOT EXISTS idx_action_logs_session_id ON action_logs(session_id);
    `);

    return db;
}

export { initializeDatabase };