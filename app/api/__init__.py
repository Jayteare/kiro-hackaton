"""
API package for expense tracker endpoints.
"""
from flask import Blueprint, jsonify
from .expenses import expenses_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Register sub-blueprints
api_bp.register_blueprint(expenses_bp)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for service monitoring.
    
    Returns:
        200: Service is healthy
        500: Service has issues
    """
    try:
        # Import here to avoid circular imports
        from app import db
        from sqlalchemy import text
        
        # Test database connection
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'service': 'expense-tracker',
            'version': '1.0.0',
            'database': 'connected'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'expense-tracker',
            'version': '1.0.0',
            'database': 'disconnected',
            'error': str(e)
        }), 500