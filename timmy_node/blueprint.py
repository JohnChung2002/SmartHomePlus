from flask import Blueprint
from .SmartDoorFlask import remote_bp

bp = Blueprint("timmy_node", __name__)
bp.register_blueprint(remote_bp)
