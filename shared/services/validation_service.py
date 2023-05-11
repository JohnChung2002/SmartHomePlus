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