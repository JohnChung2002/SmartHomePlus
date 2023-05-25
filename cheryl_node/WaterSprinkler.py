import mysql.connector
import serial 
import time 
import os
from dotenv import load_dotenv
from flask import Blueprint, Flask, render_template, redirect, url_for, request

def connect_db():
    return mysql.connector.connect(user=os.getenv("CLOUD_DATABASE_USERNAME"), password=os.getenv("CLOUD_DATABASE_PASSWORD"), host=os.getenv("CLOUD_DATABASE_HOST"), database=os.getenv("CLOUD_DATABASE_NAME"))

load_dotenv()
sprinkler_bp = Blueprint('WaterSprinkler', __name__)

# Dictionary of pins with name of pin and state ON/OFF 
pins = { 
    11: {'name' : 'PIN 11', 'state' : 0}  
} 
topic = "/cheryl_node"

def display_data():
    # Connect to the database
    db = connect_db()

    # Create a cursor object
    cur = db.cursor()

    # Execute the SQL query to retrieve data from the database
    cur.execute("SELECT * FROM systemData ORDER BY dataID DESC LIMIT 20")

    # Fetch all the rows returned by the query
    rows = cur.fetchall()

    # Close the cursor and database connection
    cur.close()
    db.close()
    
    return rows

# Main function when accessing the website 
@sprinkler_bp.route("/") 
def index():  
    # This data will be sent to index.html (pin dictionary)
    rows = display_data()
    templateData = { 
        'pins' : pins,
        'rows' : rows
    } 
    # Pass the template data into the template index.html and return it 
    return render_template('cheryl_index.html', **templateData)

 
# Function to send simple commands 
@sprinkler_bp.route("/<action>") 
def action(action): 
    if action == 'action1' : 
#         ser.write(b"1")
        client.publish(topic, "Sprinkler Off")
        pins[11]['state'] = 0 
    if action == 'action2' : 
#         ser.write(b"2")
        client.publish(topic, "Sprinkler On")
        pins[11]['state'] = 1
    if action == 'action3' : 
#         ser.write(b"3")
        client.publish(topic, "Spray at intruder")
        pins[11]['state'] = 2
#     if action == 'action4' : 
#         ser.write(b"4") 
#         pins[12]['state'] = 0
#     if action == 'action5' : 
#         ser.write(b"5") 
#         pins[12]['state'] = 1
        
    return redirect(url_for('index'))

#  This is to change the threshold value of the brightness
@sprinkler_bp.route('/submit-form', methods=['POST'])
def submit_form():
    wetnessVal = int(request.form['wetnessVal'])
    # Connect to the database
    db = connect_db()

    # Create a cursor object
    cur = db.cursor()

    # Execute the SQL query to retrieve data from the database
    sql = "UPDATE settingTable SET wetnessValue = %s WHERE tableID = 1"
    values = (wetnessVal,)
    print(wetnessVal)
    
    cur.execute(sql, values)
    
    # Commit the changes to the database
    db.commit()

    # Close the cursor and database connection
    cur.close()
    db.close()
#     return 'Form submitted successfully'
    return redirect(url_for('index'))

