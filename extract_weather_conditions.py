import os
import h2o

def extract_weather_condition_categories():
    h2o.init()
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'h2o_automl_model', 'GLM_1_AutoML_1_20250425_144833')
    model = h2o.load_model(model_path)
    # Try to find the index of weather_condition column
    col_names = model._model_json['output']['names']
    if "weather_condition" in col_names:
        idx = col_names.index("weather_condition")
        weather_condition_domain = model._model_json['output']['domains'][idx]
        print("Allowed weather_condition categories:")
        for category in weather_condition_domain:
            print(category)
    else:
        print("weather_condition column not found in model output names")

if __name__ == "__main__":
    extract_weather_condition_categories()
