import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JSON configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Request timeout settings
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=1)
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        # Security settings (loaded at runtime)
        self.SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
        
        # API settings (loaded at runtime)
        self.PAGINATION_SIZE = int(os.environ.get('PAGINATION_SIZE', 20))
        self.MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
        
        # CORS settings (for API access)
        self.CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration-specific settings."""
        pass


class DevelopmentConfig(Config):
    """Development configuration with debug features enabled."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Log SQL queries in development
    
    # Development-specific settings
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    def __init__(self):
        """Initialize development configuration with environment variables."""
        super().__init__()
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///expenses_dev.db'
    
    @staticmethod
    def init_app(app):
        """Initialize development-specific settings."""
        Config.init_app(app)
        
        # Enable detailed error pages in development
        app.config['PROPAGATE_EXCEPTIONS'] = True


class TestingConfig(Config):
    """Testing configuration optimized for test execution."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests
    SQLALCHEMY_ECHO = False  # Reduce noise in test output
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    
    # Disable pretty printing for faster tests
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    def __init__(self):
        """Initialize testing configuration with environment variables."""
        super().__init__()
        # Override some settings for testing
        self.PAGINATION_SIZE = 5  # Smaller pagination for testing
        self.MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB for tests
    
    @staticmethod
    def init_app(app):
        """Initialize testing-specific settings."""
        Config.init_app(app)
        
        # Disable logging during tests unless explicitly enabled
        import logging
        if not os.environ.get('ENABLE_TEST_LOGGING'):
            logging.disable(logging.CRITICAL)


class ProductionConfig(Config):
    """Production configuration with security and performance optimizations."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False  # Disable SQL logging in production
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance settings
    JSONIFY_PRETTYPRINT_REGULAR = False  # Faster JSON responses
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=1)  # Longer cache for static files
    
    def __init__(self):
        """Initialize production configuration with environment variables."""
        super().__init__()
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///expenses.db'
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings."""
        Config.init_app(app)
        
        # Production logging configuration
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        if not app.debug and not app.testing:
            # Ensure logs directory exists
            logs_dir = 'logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # File handler for production logs
            file_handler = RotatingFileHandler(
                'logs/expense_tracker.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Expense tracker startup')


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}