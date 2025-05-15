import os

class Config:
    """Base configuration"""
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    
    # Download settings
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 5))
    DEFAULT_BANDWIDTH_LIMIT = int(os.environ.get('DEFAULT_BANDWIDTH_LIMIT', 1024 * 1024))  # 1MB/s
    DOWNLOAD_CHUNK_SIZE = 8192  # 8KB chunks
    
    # Telegram settings (Pyrogram)
    TELEGRAM_API_ID = os.environ.get('TELEGRAM_API_ID')
    TELEGRAM_API_HASH = os.environ.get('TELEGRAM_API_HASH')
    TELEGRAM_SESSION_NAME = os.environ.get('TELEGRAM_SESSION_NAME', 'download_manager')
    TELEGRAM_PHONE = os.environ.get('TELEGRAM_PHONE')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')  # Chat to send notifications to
    TELEGRAM_ENABLED = bool(TELEGRAM_API_ID and TELEGRAM_API_HASH and TELEGRAM_PHONE)
    
    # File paths
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    CSV_FILE = os.path.join(INSTANCE_DIR, 'downloads.csv')
    SESSION_DIR = os.path.join(INSTANCE_DIR, 'sessions')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Web interface settings
    REFRESH_INTERVAL = 500  # milliseconds
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Create required directories
        os.makedirs(Config.INSTANCE_DIR, exist_ok=True)
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        os.makedirs(Config.SESSION_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add production-specific settings here

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 