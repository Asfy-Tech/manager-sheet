from flask import Blueprint

routes = Blueprint("routes", __name__)

from .web_routes import routes 
from .notification_routes import routes 
from .setting_routes import routes 
from .sheet_routes import routes 