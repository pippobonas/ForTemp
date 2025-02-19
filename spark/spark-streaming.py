"""
This script reads weather data from a Kafka topic, preprocesses it, applies a pre-trained machine learning model to make predictions, 
and writes the results back to another Kafka topic using Spark Structured Streaming.
Functions:
    - await_write_stream_kafka(df, server_kafka, topic): Writes a streaming DataFrame to a Kafka topic and waits for the termination of the query.
    - await_write_stream_console(df): Writes the given DataFrame to the console using Spark Structured Streaming and waits for the termination of the stream.
    - read_stream_kafka(session, server_kafka, topic): Reads a stream from a Kafka topic and returns a DataFrame with the value column cast to a string.
Main Execution:
    - Defines the target column for prediction.
    - Sets Kafka server and topic names for input and output.
    - Creates a Spark session.
    - Loads a pre-trained pipeline model.
    - Reads data from the input Kafka topic.
    - Parses the JSON data from the Kafka stream.
    - Preprocesses the parsed data.
    - Handles null values in the preprocessed data.
    - Applies the pre-trained model to the preprocessed data.
    - Selects relevant columns and renames the prediction column.
    - Writes the results to the output Kafka topic.
    - Stops the Spark session.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
from pyspark.ml.pipeline import PipelineModel
from utils import preprocess


# Define schema for incoming Kafka data
schema = StructType([
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("date_unix", IntegerType(), True),
    StructField("wind_speed", DoubleType(), True),
    StructField("msl", DoubleType(), True),
    StructField("tcc", DoubleType(), True),
    StructField("ssrd", DoubleType(), True),
    StructField("sp", DoubleType(), True),
    StructField("city", StringType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("2t", DoubleType(), True),
    StructField("2t_lag_1h", DoubleType(), True),
    StructField("2t_lag_2h", DoubleType(), True),
    StructField("2t_lag_3h", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

def await_write_stream_kafka(df, server_kafka, topic):
    """
    Writes a streaming DataFrame to a Kafka topic and waits for the termination of the query.
    
    Args:
        -df (DataFrame): The streaming DataFrame to be written to Kafka.
        -server_kafka (str): The Kafka bootstrap servers as a comma-separated list of host:port.
        -topic (str): The Kafka topic to which the data will be written.
    
    Returns:
        -None
    """
    
    temp=df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", server_kafka) \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .option("topic", topic) \
        .start()
    temp.awaitTermination()

def await_write_stream_console(df):
    """
    Writes the given DataFrame to the console using Spark Structured Streaming and waits for the termination of the stream.

    Parameters:
        - df (pyspark.sql.DataFrame): The DataFrame to be written to the console.

    Returns:
        - None
    """
    temp=df.writeStream \
        .format("console") \
        .start()
    temp.awaitTermination()
    
def read_stream_kafka(session,server_kafka, topic):
    """
    Reads a stream from a Kafka topic and returns a DataFrame with the value column cast to a string.
    Args:
        - session (pyspark.sql.SparkSession): The Spark session to use for reading the stream.
        - server_kafka (str): The Kafka bootstrap servers.
        - topic (str): The Kafka topic to subscribe to.
    Returns:
        - pyspark.sql.DataFrame: A DataFrame representing the stream, with the value column cast to a string.
    """
    return session \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", server_kafka) \
        .option("subscribe", topic) \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .load() \
        .selectExpr("CAST(value AS STRING) as json_str")

if __name__ == "__main__":
    
    target = "2t_future_1h"
    server_kafka = "bk1:9092"
    topic_input = f"weather-data-aggregated"
    topic_output = f"forecast-2t-1h"
    
    spark = SparkSession.builder.appName("WeatherForecastStreaming").getOrCreate()
    
    # Load the pre-trained pipeline model
    model_path = "/app/pipeline_model"
    pipeline_model = PipelineModel.load(model_path)
    
    # Read from Kafka topic1
    in_df=read_stream_kafka(spark, server_kafka, topic_input)
    
    # Parse the JSON data
    parsed_stream = in_df.select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*")
    
    # Preprocess the data
    preprocessed_stream = preprocess(parsed_stream)
    
    # Handle null values
    #preprocessed_stream = preprocessed_stream.na.drop()
    
    # Apply the pre-trained model
    predictions = pipeline_model.transform(preprocessed_stream)
    
    # Select the relevant columns to write back to Kafka
    result_stream = predictions.withColumnRenamed("prediction", target) \
        .select("city","timestamp","date_unix", "longitude", "latitude", target) \
        .withColumn("key", to_json(struct("latitude", "longitude", "date_unix"))) \
        .withColumn("value", to_json(struct("latitude", "longitude", "date_unix", "city", "timestamp", target)))
    # Write the results to Kafka topic2
    await_write_stream_kafka(result_stream, "bk1:9092", topic_output)
    spark.stop()
