import sys, re
from functools import wraps
from flask import request, render_template

def str_to_class(classname):
    return getattr(sys.modules["builtins"], classname)

def generate_missing_error(args: list):
    return f"Missing arguments: {', '.join(args)}"

def validate_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.form.get('username')
        password = request.form.get('password')
        if username is None or password is None or username == "" or password == "":
            return render_template('login.html', message="Invalid username or password"), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_john_trigger(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        appliance_id = request.form.get('appliance_id')
        status = request.form.get('status')
        if appliance_id is None or status is None or appliance_id == "" or status == "":
            return generate_missing_error(["appliance_id", "status"]), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_john_aircon_temp(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        appliance_id = request.form.get('appliance_id')
        value = request.form.get('value')
        if appliance_id is None or value is None or appliance_id == "" or value == "":
            return generate_missing_error(["appliance_id", "value"]), 400
        try:
            appliance_id = int(appliance_id)
        except:
            return "Invalid appliance id", 400
        if appliance_id not in [4, 5]:
            return "Invalid appliance_id", 400
        return f(*args, **kwargs)
    return decorated_function