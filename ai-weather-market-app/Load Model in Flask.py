# After training, integrate the model into your backend.

from flask import Flask, request, jsonify # type: ignore
import numpy as np
import tensorflow as tf # type: ignore
from sklearn.preprocessing import MinMaxScaler # type: ignore

app = Flask(__name__)

# Load trained model
model = tf.keras.models.load_model('weather_lstm.h5')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_data = np.array(data['features']).reshape(1, 10, 2)
    
    prediction = model.predict(input_data)
    return jsonify({"predicted_temperature": prediction[0][0]})

if __name__ == '__main__':
    app.run(debug=True)
