from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")
auth_public_bp = Blueprint('auth_public', __name__)

from . import (  # noqa: F401,E402
    admin,
    auth,
    projects,
    tasks,
    units,
    users,
    works,
)
