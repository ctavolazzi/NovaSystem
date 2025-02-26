"""
User model for authentication and user management.
"""
from typing import List, Optional
from sqlalchemy import Boolean, Column, String, Integer
from sqlalchemy.orm import relationship

from models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Define relationships when other models are created
    # sessions = relationship("Session", back_populates="user")

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User {self.username}>"