from flask import Blueprint, render_template, redirect, url_for, request, session, g
from discord_webhook import DiscordWebhook, DiscordEmbed
import json, os
from dotenv import load_dotenv

from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_john_trigger, validate_john_aircon_temp, validate_john_month_year

load_dotenv()

remote_bp = Blueprint('remote_trigger', __name__)
#testing remote pull

@remote_bp.route('/remote_trigger', methods=['POST'])
@auth_middleware
@validate_john_trigger
def remote_trigger():
    try:
        appliance_id = int(request.form.get('appliance_id'))
        status = int(request.form.get('status'))
        with g.dbconn:
            webhook_message = None
            g.dbconn.update("appliance_status", ["status"], ["appliance_id"], [status, appliance_id])
            if (appliance_id in [1, 2, 3]):
                message = {
                    "title": "Lights",
                    "sender": "Cloud",
                    "room": "1" if appliance_id == 1 else "Corridor" if appliance_id == 2 else "2",
                    "status": status
                }
                webhook_message = f"Light in Room {message['room']} is turned {('On' if (status == 1) else 'Off')}"
            elif (appliance_id in [4, 5]):
                message = {
                    "title": "Aircon Switch",
                    "sender": "Cloud",
                    "room": "1" if appliance_id == 4 else "2",
                    "status": status
                }
                webhook_message = f"Aircon in Room {message['room']} is turned {('On' if (status == 1) else 'Off')}"
            elif (appliance_id == 6):
                message = {
                    "title": "Ventilating Fan",
                    "sender": "Cloud",
                    "status": status
                }
                webhook_message = f"Ventilating Fan is turned {('On' if (status == 1) else 'Off')}"
            else:
                return "Error", 400
            if webhook_message is not None:
                
            webhook = DiscordWebhook(
                url=os.getenv("AUTOMATION_DISCORD_WEBHOOK"), 
                username="Home Appliance Bot"
            )
            embed = DiscordEmbed(
                title="Home Appliance Webhook", 
                description=webhook_message, 
                color="03b2f8",
                url = "https://dashboard.digitalserver.tech/"
            )
            webhook.add_embed(embed)
            webhook.execute()
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
            g.dbconn.update("appliance_status", ["status_value"], ["appliance_id"], [value, appliance_id])
            message = {
                "title": "Aircon Temp",
                "sender": "Cloud",
                "room": "1" if appliance_id == 4 else "2",
                "temp": value
            }
        g.client.publish("/john_node", json.dumps(message))
        return "Success", 200
    except:
        return "Error", 500

@remote_bp.route('/get_appliance_uptime', methods=['POST'])
@auth_middleware
@validate_john_month_year
def get_appliance_uptime():
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    with g.dbconn:
        return g.dbconn.get_appliance_uptime(month, year)