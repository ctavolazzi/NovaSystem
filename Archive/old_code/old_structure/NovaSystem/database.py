"""
Database Manager module for NovaSystem.

This module provides functionality for storing and retrieving repository run data.
"""

import os
import logging
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages persistent storage of run data, logs, and documentation.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the DatabaseManager.

        Args:
            db_path: Path to the SQLite database file. If None, uses the default path.
        """
        self.db_path = db_path or os.environ.get("NOVASYSTEM_DB_PATH", "novasystem.db")
        self.connection = None

        logger.info(f"Database manager initialized with path: {self.db_path}")

        self._connect()
        self._create_tables()

    def _connect(self) -> None:
        """
        Connect to the SQLite database.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Configure connection
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise ValueError(f"Database connection error: {str(e)}")

    def _create_tables(self) -> None:
        """
        Create database tables if they don't exist.
        """
        try:
            cursor = self.connection.cursor()

            # Runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_url TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT NOT NULL,
                    success BOOLEAN,
                    summary TEXT,
                    repository_type TEXT,
                    metadata TEXT
                )
            ''')

            # Commands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    command TEXT NOT NULL,
                    exit_code INTEGER,
                    output TEXT,
                    error TEXT,
                    execution_time REAL,
                    status TEXT,
                    timestamp TIMESTAMP,
                    command_type TEXT,
                    priority INTEGER,
                    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
                )
            ''')

            # Documentation table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documentation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
                )
            ''')

            self.connection.commit()
            logger.info("Database tables created or verified")
        except sqlite3.Error as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise ValueError(f"Database initialization error: {str(e)}")

    def create_run(self, repo_url: str, repository_type: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Create a new repository run record.

        Args:
            repo_url: URL of the repository.
            repository_type: Type of repository (e.g., python, javascript).
            metadata: Additional metadata about the repository.

        Returns:
            ID of the created run.
        """
        try:
            cursor = self.connection.cursor()

            # Convert metadata to JSON if provided
            metadata_json = json.dumps(metadata) if metadata else None

            # Insert run record
            cursor.execute('''
                INSERT INTO runs (repo_url, start_time, status, repository_type, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (repo_url, datetime.now().isoformat(), 'started', repository_type, metadata_json))

            self.connection.commit()
            run_id = cursor.lastrowid
            logger.info(f"Created run record with ID {run_id} for {repo_url}")
            return run_id
        except sqlite3.Error as e:
            logger.error(f"Error creating run record: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")

    def update_run(self, run_id: int, status: Optional[str] = None,
                  success: Optional[bool] = None, summary: Optional[str] = None,
                  end_time: bool = False) -> bool:
        """
        Update a run record.

        Args:
            run_id: ID of the run to update.
            status: New status (e.g., 'completed', 'failed').
            success: Whether the run was successful.
            summary: Summary of the run results.
            end_time: Whether to update the end_time to now.

        Returns:
            True if the update was successful, False otherwise.
        """
        try:
            cursor = self.connection.cursor()

            # Build update query
            query_parts = []
            params = []

            if status is not None:
                query_parts.append("status = ?")
                params.append(status)

            if success is not None:
                query_parts.append("success = ?")
                params.append(success)

            if summary is not None:
                query_parts.append("summary = ?")
                params.append(summary)

            if end_time:
                query_parts.append("end_time = ?")
                params.append(datetime.now().isoformat())

            if not query_parts:
                logger.warning("No fields to update in run record")
                return False

            # Construct and execute query
            query = f"UPDATE runs SET {', '.join(query_parts)} WHERE id = ?"
            params.append(run_id)

            cursor.execute(query, params)
            self.connection.commit()

            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated run record {run_id}")
            else:
                logger.warning(f"Run record {run_id} not found or not updated")

            return updated
        except sqlite3.Error as e:
            logger.error(f"Error updating run record: {str(e)}")
            return False

    def log_command(self, run_id: int, command: str, exit_code: Optional[int] = None,
                   output: Optional[str] = None, error: Optional[str] = None,
                   execution_time: Optional[float] = None, status: str = "completed",
                   command_type: Optional[str] = None, priority: Optional[int] = None) -> int:
        """
        Log a command execution.

        Args:
            run_id: ID of the run.
            command: The executed command.
            exit_code: Exit code of the command.
            output: Standard output from the command.
            error: Standard error from the command.
            execution_time: Time taken to execute the command (in seconds).
            status: Status of the execution (completed, error, timeout).
            command_type: Type of command (shell, python, etc.).
            priority: Priority of the command.

        Returns:
            ID of the created command record.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute('''
                INSERT INTO commands (run_id, command, exit_code, output, error,
                                     execution_time, status, timestamp, command_type, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (run_id, command, exit_code, output, error, execution_time,
                 status, datetime.now().isoformat(), command_type, priority))

            self.connection.commit()
            command_id = cursor.lastrowid
            logger.info(f"Logged command for run {run_id}: {command[:50]}...")
            return command_id
        except sqlite3.Error as e:
            logger.error(f"Error logging command: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")

    def store_documentation(self, run_id: int, file_path: str, content: str,
                          metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Store documentation content.

        Args:
            run_id: ID of the run.
            file_path: Path to the documentation file.
            content: Content of the documentation file.
            metadata: Additional metadata about the documentation.

        Returns:
            ID of the created documentation record.
        """
        try:
            cursor = self.connection.cursor()

            # Convert metadata to JSON if provided
            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute('''
                INSERT INTO documentation (run_id, file_path, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (run_id, file_path, content, datetime.now().isoformat(), metadata_json))

            self.connection.commit()
            doc_id = cursor.lastrowid
            logger.info(f"Stored documentation for run {run_id}: {file_path}")
            return doc_id
        except sqlite3.Error as e:
            logger.error(f"Error storing documentation: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")

    def get_run(self, run_id: int) -> Optional[Dict[str, Any]]:
        """
        Get details of a run.

        Args:
            run_id: ID of the run.

        Returns:
            Run details as a dictionary, or None if not found.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Run {run_id} not found")
                return None

            run_data = dict(row)

            # Parse metadata JSON
            if run_data.get("metadata"):
                try:
                    run_data["metadata"] = json.loads(run_data["metadata"])
                except json.JSONDecodeError:
                    logger.warning(f"Invalid metadata JSON for run {run_id}")
                    run_data["metadata"] = {}

            return run_data
        except sqlite3.Error as e:
            logger.error(f"Error getting run: {str(e)}")
            return None

    def get_commands(self, run_id: int) -> List[Dict[str, Any]]:
        """
        Get commands for a run.

        Args:
            run_id: ID of the run.

        Returns:
            List of command records.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT * FROM commands WHERE run_id = ? ORDER BY id", (run_id,))
            rows = cursor.fetchall()

            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error getting commands: {str(e)}")
            return []

    def get_documentation(self, run_id: int) -> List[Dict[str, Any]]:
        """
        Get documentation for a run.

        Args:
            run_id: ID of the run.

        Returns:
            List of documentation records.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT * FROM documentation WHERE run_id = ?", (run_id,))
            rows = cursor.fetchall()

            docs = []
            for row in dict(row):
                doc_data = dict(row)

                # Parse metadata JSON
                if doc_data.get("metadata"):
                    try:
                        doc_data["metadata"] = json.loads(doc_data["metadata"])
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid metadata JSON for documentation {doc_data['id']}")
                        doc_data["metadata"] = {}

                docs.append(doc_data)

            return docs
        except sqlite3.Error as e:
            logger.error(f"Error getting documentation: {str(e)}")
            return []

    def list_runs(self, limit: int = 10, offset: int = 0,
                 status: Optional[str] = None, success: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        List runs with filtering and pagination.

        Args:
            limit: Maximum number of runs to return.
            offset: Number of runs to skip.
            status: Filter by status.
            success: Filter by success flag.

        Returns:
            List of run records.
        """
        try:
            cursor = self.connection.cursor()

            # Build query
            query = "SELECT * FROM runs"
            params = []

            where_clauses = []
            if status is not None:
                where_clauses.append("status = ?")
                params.append(status)

            if success is not None:
                where_clauses.append("success = ?")
                params.append(success)

            if where_clauses:
                query += f" WHERE {' AND '.join(where_clauses)}"

            query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            runs = []
            for row in rows:
                run_data = dict(row)

                # Parse metadata JSON
                if run_data.get("metadata"):
                    try:
                        run_data["metadata"] = json.loads(run_data["metadata"])
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid metadata JSON for run {run_data['id']}")
                        run_data["metadata"] = {}

                runs.append(run_data)

            return runs
        except sqlite3.Error as e:
            logger.error(f"Error listing runs: {str(e)}")
            return []

    def delete_run(self, run_id: int) -> bool:
        """
        Delete a run and all associated records.

        Args:
            run_id: ID of the run to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("DELETE FROM runs WHERE id = ?", (run_id,))
            self.connection.commit()

            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted run {run_id} and all associated records")
            else:
                logger.warning(f"Run {run_id} not found or not deleted")

            return deleted
        except sqlite3.Error as e:
            logger.error(f"Error deleting run: {str(e)}")
            return False

    def delete_old_runs(self, days: int) -> int:
        """
        Delete runs older than a specified number of days.

        Args:
            days: Delete runs older than this many days.

        Returns:
            Number of deleted runs.
        """
        try:
            cursor = self.connection.cursor()

            # Calculate cutoff date
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            cutoff_date_str = datetime.fromtimestamp(cutoff_date).isoformat()

            cursor.execute("DELETE FROM runs WHERE start_time < ?", (cutoff_date_str,))
            self.connection.commit()

            deleted_count = cursor.rowcount
            logger.info(f"Deleted {deleted_count} runs older than {days} days")
            return deleted_count
        except sqlite3.Error as e:
            logger.error(f"Error deleting old runs: {str(e)}")
            return 0

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __del__(self) -> None:
        """
        Ensure database connection is closed when object is destroyed.
        """
        self.close()