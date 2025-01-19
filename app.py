import logging
from flask import Flask, jsonify, request, session, render_template, url_for, redirect, flash
import json, requests
import os
from datetime import datetime
from geopy.geocoders import Nominatim
from dotenv import load_dotenv


app = Flask(__name__)


app.secret_key = os.getenv("FLASK_SECRET_KEY")
API_KEY = os.getenv("API_SECRET_KEY")

# Set start time for uptime calculation
app.start_time = datetime.now()

# geolocation library
geofinder = Nominatim(user_agent="app")
current_city = ""
location = ""
longitude = ""
latitude = ""

load_dotenv()

# Set up log folder and log file
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_file = os.path.join(log_folder, 'app.log')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),  
        logging.StreamHandler()         
    ]
)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': str(datetime.now() - app.start_time) 
    }), 200

@app.route('/logs')
def view_logs():
    try:
        with open(log_file, 'r') as f:
            logs = f.read()

        # Serve logs as plain text
        return f"<pre>{logs}</pre>"  
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/main', methods=('GET', 'POST'))
def main():
    if request.method == 'POST':
        global current_city    
        
        state = request.form['state']
        app.logger.debug(str(state))
        
        current_city = state
        app.logger.debug('POST method reached successfully')

        if len(current_city) == 0:
            app.logger.debug('One or more required fields is missing')
            flash('One or more required fields is missing')
        else:
            app.logger.debug('POST method executed successfully')
            return redirect(url_for('result'))
    else:
        app.logger.debug('GET method executed successfully')

    return render_template('main.html')
    
@app.route('/air_index.html')
def result():
    global current_city
    if current_city is None:
        return render_template('404.html'), 404

    entry = '"'+ str(current_city)+'"'
    app.logger.debug(entry)
    
    try:
        global location
        global longitude
        global latitude
        location = geofinder.geocode(entry, timeout=10000)
        longitude = location.longitude
        latitude = location.latitude 
    except Exception as e:
        app.logger.error(f"Error geocoding location: {str(e)}")
        return render_template('404.html'), 404

    lon = str(longitude)
    lat = str(latitude)
    
    response = requests.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}")
    pollution_index = json.loads(response.text)
    
    result = pollution_index['list'][0]['main']['aqi']
    msg = None
    
    if result == 1:
        msg = 'Ideal: The Air Pollution Index is low at your location'
        app.logger.debug(msg)
    elif result == 2:
        msg = 'Fair: The Air Pollution is minimal at your location'
        app.logger.debug(msg)
    elif result == 3:
        msg = 'Moderate: The Air Pollution Index is a bit high, take precaution'
        app.logger.debug(msg)
    elif result == 4:
        msg = 'Poor: The Air Pollution Index is very high, take precaution'
        app.logger.debug(msg)
    else:
        msg = 'Emergency: The Air Pollution Index is extreme today. Report status to local authorities'
        app.logger.debug(msg)

    return render_template('result.html', msg=msg)

if __name__ == "__main__": 
    app.run(host='0.0.0.0', port=8000, debug=True)

