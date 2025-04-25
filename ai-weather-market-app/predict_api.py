from flask import jsonify

def predict_weather():
    return jsonify({
        "error": "This API is deprecated. Please use the main app.py prediction endpoints.",
        "status": "deprecated"
    }), 410

if __name__ == "__main__":
    print("This API is deprecated. Please use the main app.py prediction endpoints.")
