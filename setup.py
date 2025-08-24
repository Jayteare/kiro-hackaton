#!/usr/bin/env python3
"""
Setup script for the expense tracker application.
Run this script to set up the development environment.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("Setting up Expense Tracker development environment...")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Failed to install dependencies. Please run 'pip install -r requirements.txt' manually.")
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        try:
            with open('.env.example', 'r') as template:
                content = template.read()
            with open('.env', 'w') as env_file:
                env_file.write(content)
            print("✓ .env file created")
        except Exception as e:
            print(f"✗ Failed to create .env file: {e}")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate your virtual environment (if using one)")
    print("2. Run 'python run.py' to start the development server")
    print("3. Run 'flask init-db' to initialize the database")


if __name__ == "__main__":
    main()