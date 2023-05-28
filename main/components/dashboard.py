from flask import Blueprint, render_template, redirect, url_for, request, session, g
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_login

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@auth_middleware
def dashboard():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
    return render_template('index.html', name=user["name"])

@dashboard_bp.route("/smart_security")
def smart_door():
    # accessing database and table
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
        history = g.dbconn.get_all("history")
        rfid = g.dbconn.get_all("rfid")
        settings = g.dbconn.get_all("settings")
        stranger = g.dbconn.get_all("stranger")
    templateData = {
        'history' : history,
        'rfid' : rfid,
        'settings' : settings,
        'stranger' : stranger
    }

    # updates homepage with template content
    return render_template('smartdoor.html', **templateData, name=user["name"])

@dashboard_bp.route('/home_control', methods=['GET'])
@auth_middleware
def home_remote():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
    return render_template('home_control.html', name=user["name"])

@dashboard_bp.route("/smart_sprinkler") 
def smart_sprinkler():
    with g.dbconn:
        user = g.dbconn.get_by_id("user_details", ["user_id"], [session["user_id"]])
    return render_template('cheryl_index.html', name=user["name"])