import h2o
from h2o.estimators import H2OGeneralizedLinearEstimator
import os

def train_and_save_model():
    """
    Trains a Generalized Linear Model (GLM) using H2O and saves it to disk.

    This function initializes an H2O cluster, loads an example dataset, 
    splits it into training and validation frames, and trains a binomial 
    GLM model using specified predictors and response variables. The trained 
    model is then saved to a specified directory.

    The dataset used is a prostate cancer dataset, with 'CAPSULE' as the 
    response variable and the remaining columns as predictors.

    The trained model is saved in the 'h2o_automl_model' directory, with a 
    path that includes the model name 'GLM_1_AutoML_1_20250425_144833'.

    Raises:
        ValueError: If there is an issue with training the model or saving it.
    """

    h2o.init()

    # Load example dataset
    data = h2o.import_file("https://h2o-public-test-data.s3.amazonaws.com/smalldata/prostate/prostate.csv")
    train, valid = data.split_frame(ratios=[.8], seed=1234)

    response = "CAPSULE"
    predictors = data.columns
    predictors.remove(response)

    # Train GLM model
    model = H2OGeneralizedLinearEstimator(family="binomial")
    model.train(x=predictors, y=response, training_frame=train, validation_frame=valid)

    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), "h2o_automl_model", "GLM_1_AutoML_1_20250425_144833")
    os.makedirs(model_dir, exist_ok=True)
    model_path = h2o.save_model(model=model, path=model_dir, force=True)
    print(f"Model saved to: {model_path}")

if __name__ == "__main__":
    train_and_save_model()
