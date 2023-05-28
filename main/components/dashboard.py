from flask import Blueprint, render_template, redirect, url_for, request, session, g
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_login

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/home_control', methods=['GET'])
@auth_middleware
def home_remote():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
    return render_template('home_control.html', name=user["name"])

@dashboard_bp.route("/smart_sprinkler") 
def index():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
    return render_template('cheryl_index.html', name=user["name"])