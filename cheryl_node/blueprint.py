from flask import Blueprint
from .WaterSprinkler import sprinkler_bp

bp = Blueprint("cheryl_node", __name__)
bp.register_blueprint(sprinkler_bp)
