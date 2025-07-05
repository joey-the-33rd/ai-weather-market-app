from app.ai_model import predict_impact

def test_predict_impact():
    data = {"temp": 30, "humidity": 50, "wind": 10}
    result = predict_impact(data)
    assert result == "Increased energy demand"
