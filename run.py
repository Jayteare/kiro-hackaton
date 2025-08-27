#!/usr/bin/env python3
"""
Application startup script for the expense tracker microservice.

This script serves as the main entry point for the Flask application,
providing database initialization and development server startup.
"""
import os
import sys
import logging
from app import create_app, db


def get_config_name():
    """
    Determine configuration name from environment variables.
    
    Returns:
        str: Configuration name ('development', 'testing', 'production')
    """
    # Check multiple environment variables for configuration
    config_name = (
        os.environ.get('FLASK_ENV') or 
        os.environ.get('APP_ENV') or 
        os.environ.get('ENVIRONMENT') or 
        'development'
    )
    
    # Normalize configuration names
    config_mapping = {
        'dev': 'development',
        'test': 'testing',
        'prod': 'production',
        'production': 'production',
        'development': 'development',
        'testing': 'testing'
    }
    
    return config_mapping.get(config_name.lower(), 'development')


def setup_logging(app):
    """
    Configure application logging based on environment.
    
    Args:
        app: Flask application instance
    """
    if app.config['TESTING']:
        # Minimal logging for tests
        logging.getLogger().setLevel(logging.CRITICAL)
        return
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    if app.config['DEBUG']:
        logging.getLogger().setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)
    
    # Add handler to app logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO if not app.config['DEBUG'] else logging.DEBUG)


def initialize_database(app):
    """
    Initialize database tables and perform any necessary setup.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            app.logger.info("Database tables created successfully")
            
            # Verify database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            app.logger.info("Database connection verified")
            
        except Exception as e:
            app.logger.error(f"Database initialization failed: {str(e)}")
            raise


def create_application():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Determine configuration
    config_name = get_config_name()
    
    # Create application
    app = create_app(config_name)
    
    # Setup logging
    setup_logging(app)
    
    app.logger.info(f"Application created with {config_name} configuration")
    
    return app


# Create application instance
app = create_application()


@app.cli.command()
def init_db():
    """
    CLI command to initialize the database.
    
    Usage: flask init-db
    """
    try:
        initialize_database(app)
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)


@app.cli.command()
def reset_db():
    """
    CLI command to reset the database (drop and recreate all tables).
    
    Usage: flask reset-db
    """
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✅ Database reset successfully!")
    except Exception as e:
        print(f"❌ Database reset failed: {str(e)}")
        sys.exit(1)


@app.cli.command()
def check_config():
    """
    CLI command to display current configuration.
    
    Usage: flask check-config
    """
    print(f"Configuration: {app.config['ENV'] if 'ENV' in app.config else get_config_name()}")
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"Testing mode: {app.config['TESTING']}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Secret key set: {'Yes' if app.config['SECRET_KEY'] else 'No'}")
    print(f"Pagination size: {app.config['PAGINATION_SIZE']}")


if __name__ == '__main__':
    # Initialize database on startup for development
    if not app.config['TESTING']:
        try:
            initialize_database(app)
        except Exception as e:
            app.logger.error(f"Failed to initialize database on startup: {str(e)}")
            sys.exit(1)
    
    # Start development server
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    app.logger.info(f"Starting development server on {host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])