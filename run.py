import os
from app import create_app
from app.core.logger import main_logger

# Get environment
env = os.environ.get('FLASK_ENV', 'development')

# Create application
app = create_app(env)

if __name__ == '__main__':
    try:
        # Run application
        main_logger.info(f"Starting application in {env} mode")
        app.run(
            host='0.0.0.0',
            port=5000,
            use_reloader=False
        )
    except KeyboardInterrupt:
        main_logger.info("Application shutdown requested")
    except Exception as e:
        main_logger.error(f"Application error: {e}", exc_info=True)
    finally:
        main_logger.info("Application stopped") 