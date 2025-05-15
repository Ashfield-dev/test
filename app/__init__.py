from flask import Flask
from app.config import config
from app.core.logger import main_logger
from app.core.download_manager import DownloadManager

def create_app(config_name='default'):
    """Create Flask application"""
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize download manager
    download_manager = DownloadManager(
        max_workers=app.config['MAX_WORKERS'],
        bandwidth_limit=app.config['DEFAULT_BANDWIDTH_LIMIT']
    )
    
    # Register blueprints
    from app.web.routes.views import views
    from app.web.routes.api import api, init_api
    
    app.register_blueprint(views)
    app.register_blueprint(init_api(download_manager), url_prefix='/api')
    
    main_logger.info(f"Application started in {config_name} mode")
    
    return app 