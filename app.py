from flask import Flask, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import serial
import os
from dotenv import load_dotenv

from cheryl_node import bp_cheryl
from john_node import bp_john
from timmy_node import bp_timmy

load_dotenv()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

cors = CORS(app, resources={r"/api/*" : {"origins": "*"}})

app.register_blueprint(bp_cheryl, url_prefix='/api/node_1')
app.register_blueprint(bp_john, url_prefix='/api/node_2')
app.register_blueprint(bp_timmy, url_prefix='/api/node_3')

