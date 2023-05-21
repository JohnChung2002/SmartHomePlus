from flask import Blueprint, render_template, redirect, url_for, request, session
from flask import g
from argon2 import PasswordHasher
from shared.services.auth_middleware import auth_middleware
from shared.services.validation_service import validate_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login():
    if "user_id" in session and "user_role" in session:
        return redirect("/")
    return render_template('login.html', message=""), 200

@auth_bp.route('/login', methods=['POST'])
@validate_login
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    with g.dbconn:
        ph = PasswordHasher()
        result = g.dbconn.get_by_id("user_accounts", ["username"], [username])
        if result is not None:
            try:
                if ph.verify(result["password"], password): # type: ignore
                    session["user_id"] = result["user_id"]
                    session["user_role"] = result["role"]
                return redirect("/")
            except Exception as e:
                pass
    return render_template('login.html', message="Invalid username or password"), 401

@auth_bp.route('/logout')
@auth_middleware
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect(url_for('auth.login'))
