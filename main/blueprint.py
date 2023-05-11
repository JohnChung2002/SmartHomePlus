from flask import Blueprint
from .components.authentication import auth_bp

bp = Blueprint("main", __name__)

bp.register_blueprint(auth_bp)
