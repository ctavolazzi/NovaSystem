from typing import List, Dict, Optional
from datetime import datetime
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from nova.database import crud
from nova.database.models import Message, Session

logger = logging.getLogger(__name__)

class NovaSession:
    def __init__(self, session_id: str, user_id: str, db: AsyncSession):
        self.id = session_id
        self.user_id = user_id
        self.db = db
        self.messages: List[Dict] = []
        self._loaded = False
        self.meta_data: Dict = {}

    async def initialize(self) -> Session:
        """Initialize a new session in the database"""
        try:
            return await crud.create_session(self.db, self.id, self.user_id)
        except Exception as e:
            logger.error(f"Failed to initialize session: {str(e)}")
            raise

    async def add_message(self, role: str, content: str, model: str = None) -> Message:
        """Add a message to the session"""
        try:
            message = await crud.create_message(
                self.db,
                message_id=str(uuid.uuid4()),
                session_id=self.id,
                role=role,
                content=content,
                model=model
            )

            self.messages.append({
                "role": role,
                "content": content,
                "timestamp": message.timestamp.isoformat()
            })

            # Update session last activity
            await crud.update_session(
                self.db,
                self.id,
                {"last_activity": datetime.utcnow()}
            )

            return message
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")
            raise

    async def get_context(self) -> List[Dict]:
        """Get conversation context for LLM"""
        if not self._loaded:
            try:
                messages = await crud.get_session_messages(self.db, self.id)
                self.messages = [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in messages
                ]
                self._loaded = True
            except Exception as e:
                logger.error(f"Failed to load messages: {str(e)}")
                raise

        # Return only the role and content for LLM context
        return [{"role": m["role"], "content": m["content"]} for m in self.messages]

class SessionManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: str) -> Session:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        return await crud.create_session(self.db, session_id, user_id)

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        return await crud.get_session(self.db, session_id)

    async def end_session(self, session_id: str) -> None:
        """End a chat session"""
        await crud.update_session_status(self.db, session_id, "completed")

    async def add_message(self, session_id: str, role: str, content: str, model: str = None) -> Message:
        """Add a message to the session"""
        message_id = str(uuid.uuid4())
        return await crud.create_message(self.db, message_id, session_id, role, content, model)

    async def get_context(self, session_id: str) -> List[Dict[str, str]]:
        """Get the conversation context for a session"""
        messages = await crud.get_session_messages(self.db, session_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]