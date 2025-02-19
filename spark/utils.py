"""
This module provides utility functions for preprocessing and feature engineering on PySpark DataFrames.
The functions include adding cyclic time features, calculating wind speed and direction, and creating
windowed features for time series data.
Functions:
- preprocess(df): Preprocesses the DataFrame by adding cyclic time features and wind speed/direction features.
- add_cyclic_time_col(df, col_def, name_target, period_time): Adds cyclic time columns (sine and cosine transformations) to a DataFrame.
- add_wind_speed_deg(df): Adds wind speed and wind direction columns to the DataFrame.
- windowed_data(df): Processes the DataFrame by adding future and lagged features based on a window specification.
"""

from pyspark.sql.window import Window
from pyspark.sql.functions import sin, cos, col, lit, lead, lag, sqrt, atan2
from numpy import pi 

def preprocess(df):
    """
    Preprocess the given DataFrame by adding cyclic time features and wind speed/direction features.
    This function performs the following steps:
    1. Adds cyclic time features for daily patterns based on the 'date_unix' column.
    2. Adds cyclic time features for yearly patterns based on the 'date_unix' column.
    Parameters:
    df (Spark DataFrame): Input DataFrame containing the data to be preprocessed.
    Returns:
    Spark DataFrame: DataFrame with added cyclic time features and wind speed/direction features.
    """
    # Add cyclic time features for daily and yearly patterns
        
    SECONDS_IN_DAY = 86400
    df=add_cyclic_time_col(df,"date_unix", "day", SECONDS_IN_DAY)
    
    SECONDS_IN_YEAR = 365 * SECONDS_IN_DAY
    df=add_cyclic_time_col(df,"date_unix", "year", SECONDS_IN_YEAR)

    return df
    
def add_cyclic_time_col(df, col_def, name_target, period_time):
    """
    Adds cyclic time columns (sine and cosine transformations) to a DataFrame based on a specified time period.

    Parameters:
    df (Spark DataFrame): The input DataFrame.
    col_def (str): The name of the column in the DataFrame that contains the time values.
    name_target (str): The base name for the new cyclic time columns.
    period_time (int): The period of the cyclic time (e.g., 24 for hours in a day, 7 for days in a week).

    Returns:
    pyspark.sql.DataFrame: The DataFrame with added cyclic time columns.
    """
    df=df.withColumn(f"time_of_{name_target}", col(col_def) % lit(period_time)) \
               .withColumn(f"sine_{name_target}", sin(2 * pi * col(f"time_of_{name_target}") / lit(period_time))) \
               .withColumn(f"cosine_{name_target}", cos(2 * pi * col(f"time_of_{name_target}") / lit(period_time)))
    return df

def add_wind_speed_deg(df):
    """
    Adds wind speed and wind direction columns to the given DataFrame.

    The function calculates the wind speed using the Pythagorean theorem
    on the '10u' and '10v' columns, and the wind direction using the 
    arctangent of '10v' and '10u', converting the result to degrees.

    Parameters:
    df (DataFrame): The input DataFrame containing '10u' and '10v' columns.

    Returns:
    DataFrame: The DataFrame with added 'wind_speed' and 'wind_direction' columns.
    """
  

    df= df.withColumn("wind_speed", sqrt(col("10u")**2 + col("10v")**2)) \
               .withColumn("wind_deg", (atan2(col("10v"), col("10u")) * 180 / pi + 180) % 360)# not linear
    print("wind_speed and wind_deg added")
    return df

def windowed_data(df):
    """
    Processes the input DataFrame by adding future and lagged features based on a window specification.

    The function performs the following steps:
    1. Creates a window specification partitioned by 'latitude' and 'longitude', and ordered by 'date_unix'.
    2. Adds a new column '2t_future_1h' which contains the '2t' value 1 hour into the future.
    3. Adds lagged features for '2t' for 1, 2, and 3 hours back.
    4. Removes rows with null values caused by the lead() and lag() operations.

    Args:
        df (pyspark.sql.DataFrame): Input DataFrame containing columns 'latitude', 'longitude', 'date_unix', and '2t'.

    Returns:
        pyspark.sql.DataFrame: DataFrame with added future and lagged features, and without null values.
    """
    # Create window specification ordered by date_unix
    window_spec = Window.partitionBy("latitude", "longitude").orderBy("date_unix")

    # Add 1-hour future target for prediction
    df = df.withColumn("2t_future_1h", lead("2t", 1).over(window_spec))

    # Add lag features (1, 2, 3 hours back for better prediction)
    for lag_hour in [1, 2, 3]:
       df = df.withColumn(f"2t_lag_{lag_hour}h", lag("2t", lag_hour).over(window_spec))

    # Remove null values caused by lead() and lag()
    df = df.na.drop()
    return df