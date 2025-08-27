"""
API package for expense tracker endpoints.
"""
from flask import Blueprint
from .expenses import expenses_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Register sub-blueprints
api_bp.register_blueprint(expenses_bp)