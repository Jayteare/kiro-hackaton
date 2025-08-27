"""
Integration tests for complete application startup and configuration.

Tests the Flask application factory pattern, configuration loading,
database initialization, and overall application health.
"""
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from app import create_app, db
from config import config


class TestApplicationFactory:
    """Test the Flask application factory pattern."""
    
    def test_create_app_with_default_config(self):
        """Test creating app with default configuration."""
        app = create_app()
        
        assert app is not None
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
        assert 'PAGINATION_SIZE' in app.config
    
    def test_create_app_with_development_config(self):
        """Test creating app with development configuration."""
        app = create_app('development')
        
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False
        assert app.config['SQLALCHEMY_ECHO'] is True
        assert 'expenses_dev.db' in app.config['SQLALCHEMY_DATABASE_URI']
    
    def test_create_app_with_testing_config(self):
        """Test creating app with testing configuration."""
        app = create_app('testing')
        
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
        assert app.config['PAGINATION_SIZE'] == 5
    
    def test_create_app_with_production_config(self):
        """Test creating app with production configuration."""
        app = create_app('production')
        
        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False
        assert app.config['SQLALCHEMY_ECHO'] is False
        assert app.config['SESSION_COOKIE_SECURE'] is True
    
    def test_create_app_with_invalid_config(self):
        """Test creating app with invalid configuration falls back to default."""
        app = create_app('invalid_config')
        
        # Should fall back to default (development) configuration
        assert app.config['DEBUG'] is True


class TestConfigurationLoading:
    """Test environment-based configuration loading."""
    
    def test_config_classes_exist(self):
        """Test that all configuration classes are properly defined."""
        assert 'development' in config
        assert 'testing' in config
        assert 'production' in config
        assert 'default' in config
    
    def test_base_config_properties(self):
        """Test that base configuration has required properties."""
        from config import Config
        
        config_instance = Config()
        assert hasattr(config_instance, 'SECRET_KEY')
        assert hasattr(Config, 'SQLALCHEMY_TRACK_MODIFICATIONS')
        assert hasattr(config_instance, 'PAGINATION_SIZE')
        assert hasattr(config_instance, 'MAX_CONTENT_LENGTH')
    
    @patch.dict(os.environ, {'SECRET_KEY': 'test-secret'})
    def test_environment_variable_loading(self):
        """Test that configuration loads from environment variables."""
        app = create_app('development')
        
        assert app.config['SECRET_KEY'] == 'test-secret'
    
    @patch.dict(os.environ, {'PAGINATION_SIZE': '50'})
    def test_pagination_size_from_env(self):
        """Test pagination size loading from environment."""
        app = create_app('development')
        
        assert app.config['PAGINATION_SIZE'] == 50
    
    @patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test_custom.db'})
    def test_database_url_from_env(self):
        """Test database URL loading from environment."""
        app = create_app('development')
        
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///test_custom.db'


class TestDatabaseInitialization:
    """Test database initialization and setup."""
    
    def test_database_initialization_in_app_context(self):
        """Test that database can be initialized within app context."""
        app = create_app('testing')
        
        with app.app_context():
            # This should not raise an exception
            db.create_all()
            
            # Verify tables were created by checking if we can query
            from sqlalchemy import text
            result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
            tables = [row[0] for row in result]
            
            assert 'expenses' in tables
    
    def test_database_models_are_registered(self):
        """Test that all models are properly registered with SQLAlchemy."""
        app = create_app('testing')
        
        with app.app_context():
            # Import should not raise an exception
            from app.models.expense import Expense
            
            # Model should be in SQLAlchemy registry
            assert Expense.__tablename__ in db.metadata.tables
    
    def test_database_connection_verification(self):
        """Test database connection can be verified."""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            # This should not raise an exception
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            assert result.scalar() == 1


class TestApplicationEndpoints:
    """Test application-level endpoints and health checks."""
    
    def test_root_endpoint_exists(self):
        """Test that root endpoint provides application information."""
        app = create_app('testing')
        
        with app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['service'] == 'expense-tracker'
            assert 'version' in data
            assert 'endpoints' in data
    
    def test_health_check_endpoint_exists(self):
        """Test that health check endpoint is available."""
        app = create_app('testing')
        
        with app.test_client() as client:
            response = client.get('/health')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
            assert data['service'] == 'expense-tracker'
    
    def test_api_health_check_endpoint(self):
        """Test that API health check endpoint works."""
        app = create_app('testing')
        
        with app.app_context():
            db.create_all()
            
            with app.test_client() as client:
                response = client.get('/api/health')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'healthy'
                assert data['database'] == 'connected'


class TestErrorHandlers:
    """Test global error handlers are properly registered."""
    
    def test_404_error_handler(self):
        """Test 404 error handler returns consistent format."""
        app = create_app('testing')
        
        with app.test_client() as client:
            response = client.get('/nonexistent-endpoint')
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data
            assert data['error']['code'] == 'NOT_FOUND'
    
    def test_405_error_handler(self):
        """Test 405 error handler for method not allowed."""
        app = create_app('testing')
        
        with app.test_client() as client:
            # Try POST to GET-only endpoint
            response = client.post('/health')
            
            assert response.status_code == 405
            data = response.get_json()
            assert 'error' in data
            assert data['error']['code'] == 'METHOD_NOT_ALLOWED'


class TestApplicationIntegration:
    """Integration tests for complete application functionality."""
    
    def test_complete_application_startup_cycle(self):
        """Test complete application startup and basic functionality."""
        app = create_app('testing')
        
        # Test application creation
        assert app is not None
        
        # Test database initialization
        with app.app_context():
            db.create_all()
            
            # Test basic database operation
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            assert result.scalar() == 1
        
        # Test API endpoints are accessible
        with app.test_client() as client:
            # Test root endpoint
            response = client.get('/')
            assert response.status_code == 200
            
            # Test health check
            response = client.get('/health')
            assert response.status_code == 200
            
            # Test API health check
            response = client.get('/api/health')
            assert response.status_code == 200
    
    def test_application_with_custom_environment_config(self):
        """Test application startup with custom environment configuration."""
        with patch.dict(os.environ, {
            'SECRET_KEY': 'custom-test-key',
            'PAGINATION_SIZE': '25',
            'MAX_CONTENT_LENGTH': '2097152'  # 2MB
        }):
            app = create_app('development')
            
            assert app.config['SECRET_KEY'] == 'custom-test-key'
            assert app.config['PAGINATION_SIZE'] == 25
            assert app.config['MAX_CONTENT_LENGTH'] == 2097152
    
    def test_application_blueprints_registered(self):
        """Test that all required blueprints are registered."""
        app = create_app('testing')
        
        # Check that API blueprint is registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'api' in blueprint_names
    
    def test_application_extensions_initialized(self):
        """Test that Flask extensions are properly initialized."""
        app = create_app('testing')
        
        # Test that SQLAlchemy is initialized
        assert hasattr(app, 'extensions')
        assert 'sqlalchemy' in app.extensions
        
        # Test that Marshmallow is initialized
        assert 'flask-marshmallow' in app.extensions


class TestConfigurationSpecificBehavior:
    """Test configuration-specific application behavior."""
    
    def test_development_config_behavior(self):
        """Test development-specific configuration behavior."""
        app = create_app('development')
        
        assert app.config['DEBUG'] is True
        assert app.config['SQLALCHEMY_ECHO'] is True
        assert app.config['JSONIFY_PRETTYPRINT_REGULAR'] is True
    
    def test_production_config_behavior(self):
        """Test production-specific configuration behavior."""
        app = create_app('production')
        
        assert app.config['DEBUG'] is False
        assert app.config['SQLALCHEMY_ECHO'] is False
        assert app.config['SESSION_COOKIE_SECURE'] is True
        assert app.config['JSONIFY_PRETTYPRINT_REGULAR'] is False
    
    def test_testing_config_behavior(self):
        """Test testing-specific configuration behavior."""
        app = create_app('testing')
        
        assert app.config['TESTING'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
        assert app.config['PAGINATION_SIZE'] == 5