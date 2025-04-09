from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import json
import os
from datetime import datetime

app = Flask(__name__)

API_KEY = "7ee4289ca3374d4c88e51905250904"
MAX_CALLS_PER_MONTH = 999999
COUNTER_FILE = 'api_counter.json'

def load_counter():
    """
    Loads the API call counter from file.

    Returns:
        dict: containing 'count' (int) of the number of API calls made this month
              and 'month' (int) of the current month
    """
    if not os.path.exists(COUNTER_FILE):
        return {"count": 0, "month": datetime.now().month}
    with open(COUNTER_FILE, 'r') as f:
        return json.load(f)

def save_counter(counter):
    """
    Saves the API call counter to a file.

    Args:
        counter (dict): containing 'count' (int) of the number of API calls made this month
                        and 'month' (int) of the current month
    """
    with open(COUNTER_FILE, 'w') as f:
        json.dump(counter, f)

@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Handles GET requests to fetch current weather data for a specified city.

    This endpoint retrieves weather information from an external API based on a city
    provided as a query parameter. If no city is specified, it defaults to "Nairobi".
    
    The function tracks the number of API calls made during the current month and returns
    an error response if the monthly limit is reached. If the API call is successful, it 
    returns a JSON response containing weather details such as city name, region, country, 
    temperature, humidity, and weather condition. If the API call fails, an error message 
    is returned.

    Returns:
        flask.Response: A JSON response containing weather data or an error message.
    """

    counter = load_counter()
    current_month = datetime.now().month

    # Reset count if it's a new month
    if counter["month"] != current_month:
        counter = {"count": 0, "month": current_month}

    if counter["count"] >= MAX_CALLS_PER_MONTH:
        return jsonify({"error": "Monthly request limit reached"}), 429

    city = request.args.get('city', 'Nairobi')
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        counter["count"] += 1
        save_counter(counter)
        return jsonify({
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "temperature_c": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "condition": data["current"]["condition"]["text"]
        })
    else:
        return jsonify({"error": "Could not fetch weather data"}), 400

if __name__ == '__main__':
    app.run(debug=True)
