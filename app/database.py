"""
Database configuration and initialization for the expense tracker application.
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from app.models import Base


# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///expenses.db')

# Create engine with SQLite-specific configurations
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv('FLASK_ENV') == 'development',  # Log SQL in development
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """
    Get a database session.
    
    Returns:
        SQLAlchemy session object
    """
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.close()
        raise


def init_database():
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise


def drop_database():
    """
    Drop all database tables.
    
    Warning: This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        print("Database tables dropped successfully")
    except Exception as e:
        print(f"Error dropping database tables: {e}")
        raise


def reset_database():
    """
    Reset the database by dropping and recreating all tables.
    
    Warning: This will delete all data!
    """
    print("Resetting database...")
    drop_database()
    init_database()
    print("Database reset completed")


class DatabaseManager:
    """Database manager for handling database operations."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Create all database tables."""
        init_database()
    
    def drop_tables(self):
        """Drop all database tables."""
        drop_database()
    
    def reset_tables(self):
        """Reset all database tables."""
        reset_database()
    
    def get_session(self):
        """Get a new database session."""
        return get_db_session()
    
    def close_session(self, session):
        """Close a database session."""
        if session:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()