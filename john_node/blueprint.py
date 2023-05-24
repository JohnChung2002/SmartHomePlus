from flask import Blueprint
from .remote_trigger import remote_bp

bp = Blueprint("john_node", __name__)

bp.register_blueprint(remote_bp)