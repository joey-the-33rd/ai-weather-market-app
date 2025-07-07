# AI Models Architecture and Training Details

## 1. Introduction

This document provides an overview of the AI models used in the AI Weather Market App project. Two primary models are employed for weather prediction: a Long Short-Term Memory (LSTM) neural network and a Random Forest regressor. Both models utilize historical weather data and are trained to predict temperature based on various weather features.

## 2. Data Preprocessing

The data for both models is sourced from a PostgreSQL database containing historical weather records. Key preprocessing steps include:
- Querying relevant weather features such as temperature, humidity, wind speed, pressure, precipitation, UV index, air quality, and others.
- Handling missing values by dropping records with nulls.
- Encoding the categorical `weather_condition` feature using one-hot encoding.
- For the LSTM model, features are normalized using MinMaxScaler to scale values between 0 and 1.
- For the Random Forest model, features are used as-is after encoding.

## 3. LSTM Model Architecture and Training

The LSTM model is designed to capture temporal dependencies in sequential weather data.

### Data Preparation

- Sequences of length 10 time steps are created from the normalized feature data.
- The target variable is the temperature at the next time step.

### Model Architecture

- The model is a Keras Sequential model consisting of:
  - An LSTM layer with 64 units and `return_sequences=True`.
  - A Dropout layer with rate 0.2 to prevent overfitting.
  - A second LSTM layer with 32 units.
  - Another Dropout layer with rate 0.2.
  - A Dense output layer with 1 unit to predict temperature.

### Training

- The model is compiled with the Adam optimizer and mean squared error (MSE) loss function.
- Early stopping is used with a patience of 5 epochs to prevent overfitting.
- The model is trained for up to 50 epochs with a batch size of 32.
- Training and validation sets are split with 80% training and 20% testing.

### Saving

- The trained model is saved in HDF5 format.
- The MinMaxScaler used for normalization is saved for future data preprocessing.

## 4. Random Forest Model Training and Hyperparameter Tuning

The Random Forest model is a non-sequential regressor trained on weather features.

### Data Preparation

- Similar preprocessing as the LSTM model, including one-hot encoding of `weather_condition`.
- Features and target (temperature) are separated.

### Model Training

- The model uses `RandomForestRegressor` from scikit-learn.
- Hyperparameters tuned using GridSearchCV include:
  - Number of trees (`n_estimators`): 50, 100, 200
  - Maximum tree depth (`max_depth`): 10, 20, 30
  - Minimum samples required to split a node (`min_samples_split`): 2, 5, 10
- The best model is selected based on cross-validation performance.

### Evaluation and Saving

- The model is evaluated on a test set using mean squared error (MSE).
- The best model is saved using joblib for later use.

## 5. Model Evaluation and Saving

Both models are evaluated using mean squared error (MSE) on their respective test sets to measure prediction accuracy. The models and any necessary preprocessing objects (e.g., scalers) are saved to disk for deployment and inference.

---

This document summarizes the AI model architectures and training procedures used in the project to facilitate understanding, maintenance, and further development.
