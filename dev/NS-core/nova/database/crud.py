from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Session, Message
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# User operations
async def create_user(db: AsyncSession, user_id: str, username: str):
    """Create a new user"""
    db_user = User(
        id=user_id,
        username=username,
        created_at=datetime.utcnow(),
        meta_data={}
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: str):
    """Get a user by ID"""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

# Session operations
async def create_session(db: AsyncSession, session_id: str, user_id: str):
    """Create a new chat session"""
    db_session = Session(
        id=session_id,
        user_id=user_id,
        status="active",
        start_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        meta_data={}
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

async def get_session(db: AsyncSession, session_id: str):
    """Get a session by ID"""
    result = await db.execute(select(Session).filter(Session.id == session_id))
    return result.scalar_one_or_none()

async def update_session_status(db: AsyncSession, session_id: str, status: str):
    """Update a session's status"""
    session = await get_session(db, session_id)
    if session:
        session.status = status
        session.last_activity = datetime.utcnow()
        await db.commit()
    return session

# Message operations
async def create_message(
    db: AsyncSession,
    message_id: str,
    session_id: str,
    role: str,
    content: str,
    model: str = None,
    tokens_used: int = None
) -> Message:
    try:
        message = Message(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            model=model,
            tokens_used=tokens_used
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message
    except Exception as e:
        logger.error(f"Failed to create message: {str(e)}")
        await db.rollback()
        raise

async def get_session_messages(db: AsyncSession, session_id: str) -> List[Message]:
    try:
        result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.timestamp)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Failed to get session messages: {str(e)}")
        raise