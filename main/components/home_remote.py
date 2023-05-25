from flask import Blueprint, render_template, redirect, url_for, request, session
from flask import g
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_login

home_remote_bp = Blueprint('home_remote', __name__)

@home_remote_bp.route('/home_remote', methods=['GET'])
@auth_middleware
def home_remote():
    return render_template('home_remote.html'), 200