from flask import Flask

app = Flask(__name__)

from . import main, ai_model, weather_data  # import other modules as needed

# You can also initialize extensions or blueprints here if applicable
