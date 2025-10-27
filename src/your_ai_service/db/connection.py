"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from ..config import settings
from .models import Base


class DatabaseManager:
    """Database connection manager."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database connection and create tables."""
        if settings.database_url.startswith("sqlite"):
            # SQLite specific configuration
            self.engine = create_engine(
                settings.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            # For other databases (PostgreSQL, MySQL, etc.)
            self.engine = create_engine(settings.database_url)
        
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Session:
    """Dependency function for FastAPI to get database session."""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
