from flask import Flask, render_template, jsonify, request
from app.web.routes import routes, guests
from app.monitors.file_watcher import FileWatcher
from config.settings import settings
from app.models.base import db_session
import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, 'app.log')

        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)
            handler.close()

        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=10, delay=True, encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        console_handler.setLevel(logging.DEBUG)

        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)  # Đặt mức log phù hợp

        return True
    except Exception as e:
        # print(f"Error configuring logging: {e}")
        return False


def create_app():
    app = Flask(
        __name__, 
        static_folder=str(settings.STATIC_DIR),
        template_folder=str(settings.TEMPLATES_DIR)
    )
    app.secret_key = settings.APP_KEY
    app.config["UPLOAD_FOLDER"] = settings.UPLOAD_FOLDER

    
    # Configure app
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    app.register_blueprint(guests)
    app.register_blueprint(routes)

    # Add error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {error}')
        return render_template('errors/404.html'), 404

    @app.errorhandler(500) 
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500
        
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.error(f'Bad request: {error}')
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400
        
    # @app.before_request
    # def before_request():
    #     # Add request logging
    #     app.logger.info(f"Request: {request.method} {request.url}")
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
