from flask import Blueprint, render_template, redirect, url_for, request, session
from flask import g
import json

from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_john_trigger, validate_john_aircon_temp

remote_bp = Blueprint('remote_trigger', __name__)

@remote_bp.route('/remote_trigger', methods=['POST'])
@auth_middleware
@validate_john_trigger
def remote_trigger():
    try:
        appliance_id = int(request.form.get('appliance_id'))
        status = int(request.form.get('status'))
        with g.dbconn:
            g.dbconn.update("appliance_status", ["status"], ["appliance_id"], [status, appliance_id])
            if (appliance_id in [1, 2, 3]):
                message = {
                    "title": "Lights",
                    "sender": "Cloud",
                    "room": "1" if appliance_id == 1 else "Corridor" if appliance_id == 2 else "2",
                    "status": status
                }
            elif (appliance_id in [4, 5]):
                message = {
                    "title": "Aircon Switch",
                    "sender": "Cloud",
                    "room": "1" if appliance_id == 4 else "2",
                    "status": status
                }
            elif (appliance_id == 6):
                message = {
                    "title": "Ventilating Fan",
                    "sender": "Cloud",
                    "status": status
                }
            else:
                return "Error", 400
            g.client.publish("/john_node", json.dumps(message))
        return "Success", 200
    except:
        return "Error", 500
    
@remote_bp.route('/remote_aircon_temp', methods=['POST'])
@auth_middleware
@validate_john_aircon_temp
def remote_aircon_temp():
    try:
        appliance_id = int(request.form.get('appliance_id'))
        value = int(request.form.get('value'))
        with g.dbconn:
            g.dbconn.update("appliance_status", ["status_value"], ["appliance_id"], [value, 4])
            message = {
                "title": "Aircon Temp",
                "sender": "Cloud",
                "room": "4" if appliance_id == 4 else "5",
                "temp": value
            }
            g.client.publish("/john_node", json.dumps(message))
        return "Success", 200
    except:
        return "Error", 500
