from flask import Blueprint

routes = Blueprint("routes", __name__)

from . import web_routes, sheet_routes