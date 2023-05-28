from flask import Blueprint, render_template, redirect, url_for, request, session, g
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_login

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@auth_middleware
def dashboard():
    with g.dbconn:
        user = g.dbconn.get_by_id("Profile", ["profile_id"], [session["user_id"]])
    return render_template('index.html', name=user["name"])

@dashboard_bp.route("/smart_security")
def smart_door():
    # accessing database and table
    with g.dbconn:
        user = g.dbconn.get_by_id("Profile", ["profile_id"], [session["user_id"]])
        settings = g.dbconn.get_all("Settings")
    # updates homepage with template content
    print(settings)
    return render_template('smartdoor.html', name=user["name"], settings=settings[0])

@dashboard_bp.route('/home_control', methods=['GET'])
@auth_middleware
def home_remote():
    with g.dbconn:
        user = g.dbconn.get_by_id("Profile", ["profile_id"], [session["user_id"]])
    return render_template('home_control.html', name=user["name"])

@dashboard_bp.route("/smart_sprinkler") 
@auth_middleware
def smart_sprinkler():
    with g.dbconn:
        user = g.dbconn.get_by_id("Profile", ["profile_id"], [session["user_id"]])
    return render_template('cheryl_index.html', name=user["name"])

@dashboard_bp.route("/profile")
@auth_middleware
def profile():
    with g.dbconn:
        user = g.dbconn.get_by_id("Profile", ["profile_id"], [session["user_id"]])
        iata_region = g.dbconn.get_by_id("config", ["field"], ["iata_region"])
    return render_template('profile.html', name=user["name"], role=session["user_role"], birthday=user["birthday"], weight=user['weight'], height=user['height'], iata_region=iata_region["value"])
