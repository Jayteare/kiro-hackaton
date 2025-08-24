from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import config

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Register blueprints (will be added in later tasks)
    # from app.api import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')
    
    return app