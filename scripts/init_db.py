#!/usr/bin/env python3
"""
Database initialization script for the expense tracker application.

This script creates the database tables and can be used for initial setup
or resetting the database during development.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import init_database, reset_database, drop_database


def main():
    """Main function to handle database initialization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database initialization script')
    parser.add_argument(
        '--reset', 
        action='store_true', 
        help='Reset database (drop and recreate all tables)'
    )
    parser.add_argument(
        '--drop', 
        action='store_true', 
        help='Drop all database tables'
    )
    
    args = parser.parse_args()
    
    try:
        if args.reset:
            print("Resetting database...")
            reset_database()
        elif args.drop:
            print("Dropping database tables...")
            drop_database()
        else:
            print("Initializing database...")
            init_database()
        
        print("Database operation completed successfully!")
        
    except Exception as e:
        print(f"Error during database operation: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()