"""Test basic application structure and configuration."""

import pytest
from app import create_app, db


def test_app_creation():
    """Test that the app can be created with different configurations."""
    # Test development config
    dev_app = create_app('development')
    assert dev_app is not None
    assert dev_app.config['DEBUG'] is True
    
    # Test testing config
    test_app = create_app('testing')
    assert test_app is not None
    assert test_app.config['TESTING'] is True
    
    # Test production config
    prod_app = create_app('production')
    assert prod_app is not None
    assert prod_app.config['DEBUG'] is False


def test_database_initialization(app):
    """Test that database can be initialized."""
    with app.app_context():
        # Database should be created by conftest.py fixture
        assert db.engine is not None


def test_config_values(app):
    """Test that configuration values are set correctly."""
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['PAGINATION_SIZE'] == 5