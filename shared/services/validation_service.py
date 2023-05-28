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
        appliance_id_invalid = appliance_id is None or appliance_id == ""
        value_invalid = value is None or value == ""
        if (appliance_id_invalid or value_invalid):
            missing = []
            if appliance_id_invalid:
                missing.append("appliance_id")
            if value_invalid:
                missing.append("value")
            return generate_missing_error(missing), 400
        try:
            appliance_id = int(appliance_id)
            if appliance_id not in [4, 5]:
                raise Exception()
        except:
            return "Invalid appliance id", 400
        return f(*args, **kwargs)
    return decorated_function

def validate_john_month_year(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        month = request.form.get('month')
        year = request.form.get('year')
        month_invalid = month is None or month == ""
        year_invalid = year is None or year == ""
        if (month_invalid or year_invalid):
            missing = []
            if month_invalid:
                missing.append("month")
            if year_invalid:
                missing.append("year")
            return generate_missing_error(missing), 400
        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12 or year < 0:
                raise Exception()
        except:
            return "Invalid month or year", 400
        return f(*args, **kwargs)
    return decorated_function

def validate_timmy_settings(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        door_height = request.form.get('door-height')
        in_distance_threshold = request.form.get('in-distance-threshold')
        out_distance_threshold = request.form.get('out-distance-threshold')
        closing_duration = request.form.get('closing-duration')
        detection_duration = request.form.get('detection-duration')
        face_detection_duration = request.form.get('face-detection-duration')
        door_height_invalid = door_height is None or door_height == ""
        in_distance_threshold_invalid = in_distance_threshold is None or in_distance_threshold == ""
        out_distance_threshold_invalid = out_distance_threshold is None or out_distance_threshold == ""
        closing_duration_invalid = closing_duration is None or closing_duration == ""
        detection_duration_invalid = detection_duration is None or detection_duration == ""
        face_detection_duration_invalid = face_detection_duration is None or face_detection_duration == ""
        if (door_height_invalid or in_distance_threshold_invalid or out_distance_threshold_invalid or closing_duration_invalid or detection_duration_invalid or face_detection_duration_invalid):
            missing = []
            if door_height_invalid:
                missing.append("door-height")
            if in_distance_threshold_invalid:
                missing.append("in-distance-threshold")
            if out_distance_threshold_invalid:
                missing.append("out-distance-threshold")
            if closing_duration_invalid:
                missing.append("closing-duration")
            if detection_duration_invalid:
                missing.append("detection-duration")
            if face_detection_duration_invalid:
                missing.append("face-detection-duration")
            return generate_missing_error(missing), 400
        try:
            door_height = int(door_height)
            in_distance_threshold = int(in_distance_threshold)
            out_distance_threshold = int(out_distance_threshold)
            closing_duration = int(closing_duration)
            detection_duration = int(detection_duration)
            face_detection_duration = int(face_detection_duration)
        except:
            return "Invalid settings", 400
        return f(*args, **kwargs)
    return decorated_function