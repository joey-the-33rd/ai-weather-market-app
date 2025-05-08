import h2o
import os

def inspect_model_schema():
    # Initialize H2O
    h2o.init()

    # Load the model
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'h2o_automl_model', 'GLM_1_AutoML_1_20250425_144833')
    model = h2o.load_model(model_path)

    # Get model input names
    input_columns = model._model_json['output']['names']
    print("Model input columns:")
    for col in input_columns:
        print(f" - {col}")

    # Get domain values for categorical columns
    print("\nCategorical columns and their domain values:")
    domains = model._model_json['output']['domains']
    for col, domain in zip(input_columns, domains):
        if domain:
            print(f" - {col}: {domain}")

if __name__ == "__main__":
    inspect_model_schema()
