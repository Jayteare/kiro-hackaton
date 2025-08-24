#!/usr/bin/env python3
"""
Verification script to ensure the Flask expense tracker setup is working correctly.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from app import create_app, db, ma
        from config import config
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that Flask apps can be created with different configurations."""
    try:
        from app import create_app
        
        # Test all configurations
        configs = ['development', 'testing', 'production']
        for config_name in configs:
            app = create_app(config_name)
            assert app is not None
            print(f"✅ {config_name.capitalize()} app created successfully")
        
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_database_setup():
    """Test that database can be initialized."""
    try:
        from app import create_app, db
        
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            print("✅ Database initialization successful")
        
        return True
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🔍 Verifying Flask Expense Tracker Setup...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("App Creation Tests", test_app_creation),
        ("Database Setup Tests", test_database_setup)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All verification tests passed!")
        print("\nYour Flask expense tracker is ready for development!")
        print("\nNext steps:")
        print("1. Run 'python run.py' to start the development server")
        print("2. Run 'python -m pytest' to run all tests")
        print("3. Begin implementing the next task in the task list")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()