from flask import Blueprint
from app.middlewares import login_required

routes = Blueprint("routes", __name__)
guests = Blueprint("guests", __name__)

@routes.before_request
def check_login():
    return login_required(lambda: None)()

from .guest_routes import guests 
from .web_routes import routes 
from .notification_routes import routes 
from .setting_routes import routes 
from .sheet_routes import routes 
from .tele_user_routes import routes 
from .notification import routes
from .template_routes import routes