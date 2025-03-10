from flask import Flask, render_template
from app.web.routes import routes
from app.monitors.file_watcher import FileWatcher
from config.settings import settings
import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up file handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))

    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

def create_app():
    app = Flask(
        __name__, 
        static_folder=str(settings.STATIC_DIR),
        template_folder=str(settings.TEMPLATES_DIR)
    )
    
    # Configure app
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    app.register_blueprint(routes)

    # Add error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {error}')
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/404.html'), 500
    
    return app

def main():
    app = create_app()
    watcher = FileWatcher(interval=settings.SYNC_INTERVAL)
    
    try:
        watcher.start()
        app.run(debug=True, use_reloader=True)
    finally:
        watcher.stop()

if __name__ == "__main__":
    main()
