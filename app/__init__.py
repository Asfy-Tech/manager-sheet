from flask import Flask
from config.settings import settings

def create_app():
    app = Flask(
        __name__,
        static_folder=str(settings.STATIC_DIR),
        template_folder=str(settings.TEMPLATES_DIR)
    )

    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'

    # Register blueprints
    from app.web.routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app