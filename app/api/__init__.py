from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from . import auth, users, units, projects, tasks, admin, works
