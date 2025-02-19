"""
This script performs weather prediction using PySpark's machine learning library. It includes functions for training
a linear regression model with and without hyperparameter tuning, as well as testing the trained model.
Global Variables:
    - target_column (str): The name of the target column for prediction.
    - feature_columns (list): A list of feature column names used for training the model.
Functions:
    - train_with_tuning(df, pipeline, polyExpansion, lr): Trains a machine learning model with hyperparameter tuning using cross-validation.
    - train_without_tuning(df, pipeline): Trains a machine learning model using a given pipeline without hyperparameter tuning.
    - train(df, with_tuning=False): Trains a linear regression model on the given DataFrame with optional hyperparameter tuning.
    - test(df): Test the model on the given DataFrame.
Main Execution:
    - Initializes a Spark session.
    - Loads the CSV dataset.
    - Trains the model.
    - Tests the model.
    - Stops the Spark session.
"""

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler, PolynomialExpansion
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.pipeline import PipelineModel
import os
from utils import preprocess, windowed_data, add_wind_speed_deg
from pyspark import StorageLevel

# Global variables
target_column = "2t_future_1h"  # Target is temperature 1 hour ahead

feature_columns = [
    "latitude", "longitude",
    "wind_speed",
    "msl", "sp", "ssrd", "tcc", "date_unix",
    "sine_day", "cosine_day", "sine_year", "cosine_year",
    "time_of_day", "time_of_year", "2t",
    "2t_lag_1h", "2t_lag_2h", "2t_lag_3h"
]

def train_with_tuning(df, pipeline, polyExpansion, lr):
    """
    Train a machine learning model with hyperparameter tuning using cross-validation.
    Parameters:
    df (DataFrame): The input Spark DataFrame containing the data.
    pipeline (Pipeline): The Spark ML pipeline to be used for training.
    polyExpansion (PolynomialExpansion): The polynomial expansion stage in the pipeline.
    lr (LinearRegression): The linear regression stage in the pipeline.
    Returns:
    None
    This function performs the following steps:
    1. Persists the input DataFrame to memory and disk.
    2. Splits the DataFrame into training and test sets.
    3. Defines a parameter grid for hyperparameter tuning.
    4. Sets up cross-validation with the specified pipeline and parameter grid.
    5. Trains the model using cross-validation.
    6. Retrieves the best model from the cross-validation results.
    7. Saves the best model to disk.
    8. Prints the best model's parameters and performance metrics (RMSE and R²).
    """
    # Persist data
    df.persist(StorageLevel.MEMORY_AND_DISK)
    
    # Split dataset into training and test sets
    train_data, test_data = df.randomSplit([0.8, 0.2])
    
    # Parameter grid for cross-validation tuning
    paramGrid = ParamGridBuilder() \
        .addGrid(polyExpansion.degree, [2, 3]) \
        .addGrid(lr.regParam, [0.1, 0.01, 0.001]) \
        .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0]) \
        .build()

    # Cross-validation setup
    crossval = CrossValidator(estimator=pipeline,
                              estimatorParamMaps=paramGrid,
                              evaluator=RegressionEvaluator(labelCol=target_column),
                              numFolds=3)

    # Train the model using cross-validation
    cvModel = crossval.fit(train_data)

    # Get the best model
    best_model = cvModel.bestModel

    # Save the best model to disk
    if best_model:
        best_model.write().overwrite().save(model_path)

        print(f"Best model parameters: \n"
              f"Polynomial degree: {best_model.stages[1].getDegree()}\n"
              f"Regularization parameter: {best_model.stages[3].getRegParam()}\n"
              f"Elastic net parameter: {best_model.stages[3].getElasticNetParam()}")
        print(f"Best model RMSE: {best_model.stages[-1].summary.rootMeanSquaredError}")
        print(f"Best model R²: {best_model.stages[-1].summary.r2}")

def train_without_tuning(df, pipeline):
    """
    Trains a machine learning model using a given pipeline without hyperparameter tuning.
    Args:
    df (DataFrame): The input DataFrame containing the dataset.
    pipeline (Pipeline): The machine learning pipeline to be used for training.
    Returns:
    None
    
    This function performs the following steps:
    1. Splits the input dataset into training and test sets.
    2. Fits the pipeline to the training data.
    3. Saves the trained model to the specified path.
    4. Evaluates the model on the test data using RMSE and R² metrics.
    5. Prints the evaluation metrics.
    """
    # Split dataset into training and test sets
    train_data, test_data = df.randomSplit([0.8, 0.2])

    model = pipeline.fit(train_data)
    
    model.write().overwrite().save(model_path)
    
    # Evaluate the model
    predictions = model.transform(test_data)
    evaluator = RegressionEvaluator(labelCol=target_column, predictionCol="prediction", metricName="rmse")

    rmse = evaluator.evaluate(predictions)
    r2 = evaluator.setMetricName("r2").evaluate(predictions)
    
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"R²: {r2}")

def train(df, with_tuning=False):
    """
    Trains a linear regression model on the given DataFrame with optional hyperparameter tuning.
    Parameters:
        - df (DataFrame): The input Spark DataFrame containing the dataset to be used for training.
        - with_tuning (bool): If True, performs hyperparameter tuning on the model. Defaults to False.
    Returns:
        - Model: The trained linear regression model, with or without hyperparameter tuning based on the with_tuning parameter.
    """
    # Preprocess the dataset
    df = windowed_data(df)
    df = preprocess(df)
    df = add_wind_speed_deg(df)

    # Assemble features into a single vector
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")

    # Polynomial Expansion (feature transformation)
    polyExpansion = PolynomialExpansion(inputCol="features", outputCol="polyFeatures")

    # Standardization
    scaler = StandardScaler(inputCol="polyFeatures", outputCol="scaledFeatures")

    # Linear Regression model
    lr = LinearRegression(featuresCol="scaledFeatures", labelCol=target_column)

    # Create a pipeline with all steps
    pipeline = Pipeline(stages=[assembler, polyExpansion, scaler, lr])
    
    if with_tuning:
        return train_with_tuning(df, pipeline, polyExpansion, lr)
    else:
        return train_without_tuning(df, pipeline)

def test(df):
    """
    Preprocesses the input DataFrame, loads a pre-trained pipeline model, and makes future predictions.
    Args:
        df (pyspark.sql.DataFrame): Input DataFrame to be processed and used for predictions.
    Returns:
        None: The function displays the top 10 rows of the future predictions DataFrame.
    """
    
    # Preprocess the dataset
    df = windowed_data(df)
    df = add_wind_speed_deg(df)
    df = preprocess(df)
    
    # Load the pre-trained pipeline model
    loaded_pipeline_model = PipelineModel.load(model_path)
    
    # Make future predictions
    future_predictions = loaded_pipeline_model.transform(df)

    future_predictions.show(10)

if __name__ == "__main__":
    spark = SparkSession.builder.appName("WeatherPredictionChain").getOrCreate()
    
    # Load the CSV dataset
    app_path = os.getenv("APP_PATH", "/app")  # Application path
    data_path = os.path.join(app_path, "dati", "output.csv")  # CSV path
    model_path = os.path.join(app_path, "pipeline_model")  # Model path
    
    data = spark.read.csv(data_path, header=True, inferSchema=True)
    
    if data is not None:
        train(data, with_tuning=False)
        test(data)
    else:
        print("Failed to load data.")
    
    spark.stop()