from flask import Blueprint
from .components.authentication import auth_bp
from .components.dashboard import dashboard_bp

bp = Blueprint("main", __name__)

bp.register_blueprint(auth_bp)
bp.register_blueprint(dashboard_bp)
