from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import config
import logging

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()


def create_app(config_name='default'):
    """
    Application factory pattern for creating Flask application instances.
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = config.get(config_name, config['default'])
    config_obj = config_class()  # Create instance at runtime
    app.config.from_object(config_obj)
    
    # Initialize configuration-specific settings
    config_obj.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Configure logging (basic setup, enhanced in run.py)
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import expense
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Add root health check endpoint
    @app.route('/health')
    def root_health_check():
        """Root level health check endpoint."""
        return {
            'status': 'healthy',
            'service': 'expense-tracker',
            'version': '1.0.0'
        }
    
    # Add application info endpoint
    @app.route('/')
    def app_info():
        """Application information endpoint."""
        return {
            'service': 'expense-tracker',
            'version': '1.0.0',
            'description': 'Expense tracking microservice API',
            'endpoints': {
                'health': '/health',
                'api_health': '/api/health',
                'expenses': '/api/expenses',
                'categories': '/api/categories',
                'summary': '/api/expenses/summary'
            }
        }
    
    return app


def register_error_handlers(app):
    """Register global error handlers for consistent error responses."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            'error': {
                'code': 'BAD_REQUEST',
                'message': 'Bad request'
            }
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'Method not allowed for this endpoint'
            }
        }), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors."""
        return jsonify({
            'error': {
                'code': 'REQUEST_TOO_LARGE',
                'message': 'Request payload too large'
            }
        }), 413
    
    @app.errorhandler(415)
    def unsupported_media_type(error):
        """Handle 415 Unsupported Media Type errors."""
        return jsonify({
            'error': {
                'code': 'UNSUPPORTED_MEDIA_TYPE',
                'message': 'Unsupported media type'
            }
        }), 415
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors."""
        return jsonify({
            'error': {
                'code': 'UNPROCESSABLE_ENTITY',
                'message': 'Unprocessable entity'
            }
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        app.logger.error(f'Internal server error: {str(error)}')
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Internal server error'
            }
        }), 500
    
    @app.before_request
    def validate_content_length():
        """Validate request content length to prevent oversized requests."""
        max_content_length = app.config.get('MAX_CONTENT_LENGTH')
        if max_content_length is None:
            max_content_length = 16 * 1024 * 1024  # 16MB default
        
        if request.content_length and request.content_length > max_content_length:
            return jsonify({
                'error': {
                    'code': 'REQUEST_TOO_LARGE',
                    'message': f'Request payload exceeds maximum size of {max_content_length} bytes'
                }
            }), 413