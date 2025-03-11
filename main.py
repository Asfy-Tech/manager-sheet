from flask import Flask, render_template, jsonify, request
from app.web.routes import routes
from app.monitors.file_watcher import FileWatcher
from config.settings import settings
import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    try:
        # Tạo thư mục logs nếu chưa tồn tại
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, 'app.log')

        # Xóa handlers cũ
        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)
            handler.close()

        # Tạo file handler mới
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=10,
            delay=True,  # Delay creation until first write
            encoding='utf-8'
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # Add handlers
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        
        return True
    except Exception as e:
        print(f"Error configuring logging: {e}")
        return False

def create_app():
    app = Flask(__name__, 
                static_folder=str(settings.STATIC_DIR),
                template_folder=str(settings.TEMPLATES_DIR))
    
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
        return render_template('errors/500.html'), 500
        
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.error(f'Bad request: {error}')
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400
        
    @app.before_request
    def before_request():
        # Add request logging
        app.logger.info(f"Request: {request.method} {request.url}")
    
    return app

def main():
    app = create_app()

    # if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #     watcher = FileWatcher(interval=settings.SYNC_INTERVAL)
    #     watcher.start()

    try:
        app.run(debug=True, use_reloader=True)
    finally:
        pass
        # watcher.stop()

if __name__ == "__main__":
    main()
