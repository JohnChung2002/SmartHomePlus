from flask import Blueprint
from .components.authentication import auth_bp
from .components.home_remote import home_remote_bp

bp = Blueprint("main", __name__)

bp.register_blueprint(auth_bp)
bp.register_blueprint(home_remote_bp)
