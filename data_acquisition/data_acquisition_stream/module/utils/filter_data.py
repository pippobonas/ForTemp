import math
import time
import datetime

"""
This module provides functions to process and normalize meteorological data.
Functions:
    unix_to_day_of_year(unix_timestamp, timezone_shift=0):
    unix_to_local_time(unix_timestamp, timezone_shift=0):
    calculate_solar_radiation(cloud_cover, latitude, day_of_year, local_time):
    total_precipitation(rain, snow):
        Calculate the total precipitation by summing rain and snow.
    convert_unix_time_to_date(unix_timestamp):
        Convert a Unix timestamp to a date string in the format 'YYYY-MM-DD'.
    time_converter_unix_to_time(unix_timestamp):
        Convert a Unix timestamp to a time string in the format 'HH:MM:SS'.
    convert_percent_to_decimal(percent):
        Convert a percentage value to a decimal.
    convert_hpa_to_pa(pressure_hpa):
        Convert pressure from hectopascals (hPa) to pascals (Pa).
    filter_data(data):
        Filter and extract relevant meteorological data from a raw data dictionary.
    normalize_data(filtered):
        Normalize the filtered meteorological data to apipeline format.
"""

# Functions to normalize data to CDS reference values



# Function to convert Unix timestamp to day of the year
def unix_to_day_of_year(unix_timestamp, timezone_shift=0):
    """
    Convert a Unix timestamp to the day of the year, considering an optional timezone shift.
    Args:
        unix_timestamp (int): The Unix timestamp to convert.
        timezone_shift (int, optional): The timezone offset in seconds. Defaults to 0.
    Returns:
        int: The day of the year (1-365 or 1-366 for leap years).
    """

    # Apply the time zone offset in seconds (create a timedelta object)
    tz_offset = datetime.timedelta(seconds=timezone_shift)
    
    # Convert the Unix timestamp to a datetime object with the shift applied
    dt = datetime.datetime.fromtimestamp(unix_timestamp, tz=datetime.timezone.utc) + tz_offset
    
    # Return the day of the year (1-365 or 1-366 for leap years)
    return dt.timetuple().tm_yday

# Function to convert Unix timestamp to local time in decimal hours
def unix_to_local_time(unix_timestamp, timezone_shift=0):
    """
    Convert a Unix timestamp to local time in decimal hours.
    Args:
        unix_timestamp (int): The Unix timestamp to convert.
        timezone_shift (int, optional): The time zone offset in seconds. Defaults to 0.
    Returns:
        float: The local time in decimal hours.
    """
    # Apply the time zone offset in seconds (create a timedelta object)
    tz_offset = datetime.timedelta(seconds=timezone_shift)
    
    # Convert the Unix timestamp to a datetime object with the shift applied
    dt = datetime.datetime.fromtimestamp(unix_timestamp, tz=datetime.timezone.utc) + tz_offset
    
    # Extract hours, minutes, and seconds
    hours = dt.hour
    minutes = dt.minute
    seconds = dt.second
    
    # Calculate the time in decimal hours
    local_time_decimal = hours + minutes / 60 + seconds / 3600
    return local_time_decimal

# Function to estimate surface solar radiation
def calculate_solar_radiation(cloud_cover, latitude, day_of_year, local_time):
    """
    Calculate the solar radiation in Joules per square meter (J/m²) based on cloud cover, latitude, day of the year, and local time.
    Parameters:
    cloud_cover (float): The percentage of cloud cover (0 to 100).
    latitude (float): The latitude of the location in degrees.
    day_of_year (int): The day of the year (1 to 365).
    local_time (float): The local time in hours (0 to 24).
    Returns:
    float: The estimated solar radiation in Joules per square meter (J/m²). Returns 0 if the calculated value is negative.(is not possible to have negative solar radiation)# is night
    """
    I0 = 1366.9  # Average extraterrestrial solar irradiance (W/m²)
    
    # Calculation of solar declination
    declination = 23.45 * math.sin(math.radians((360 / 365) * (284 + day_of_year)))
    
    # Calculation of the zenith angle
    hour_angle = (local_time - 12) * 15  # 15° for each hour from noon
    latitude_rad = math.radians(latitude)
    declination_rad = math.radians(declination)
    cos_theta_z = math.sin(latitude_rad) * math.sin(declination_rad) + \
                  math.cos(latitude_rad) * math.cos(declination_rad) * math.cos(math.radians(hour_angle))
    
    # Estimate of solar radiation with cloud cover correction
    solar_radiation_w_m2 = I0 * (1 - 0.75 * (cloud_cover / 100)**3) * cos_theta_z
    solar_radiation_j_m2 = solar_radiation_w_m2 * 3600  # Convert to J/m²
    return solar_radiation_j_m2 if solar_radiation_j_m2 > 0 else 0

# Function to calculate total precipitation
def total_precipitation(rain, snow):
    """
    Calculate the total precipitation by summing the rain and snow values.
    Parameters:
    rain (float): The amount of rain in millimeters.
    snow (float): The amount of snow in millimeters.
    Returns:
    float: The total precipitation in millimeters.
    """
    return rain + snow


# Function to convert Unix timestamp to time
def time_converter_unix_to_time(unix_timestamp):
    """
    Convert a Unix timestamp to a human-readable time string.
    Args:
        unix_timestamp (int): The Unix timestamp to convert.
    Returns:
        str: The converted time in 'HH:MM:SS' format.
    """

    return time.strftime('%H:%M:%S', time.localtime(unix_timestamp))

# Function to convert percentage to decimal
def convert_percent_to_decimal(percent):
    """
    Convert a percentage value to a decimal.
    Args:
        percent (float): The percentage value to convert.
    Returns:
        float: The decimal representation of the percentage.
    """

    return percent / 100

def convert_percent_to_micromicromillesimal(percent):
    """
    Convert a percentage value to a micromillesimal.
    Args:
        percent (float): The percentage value to convert.
    Returns:
        float: The micromillesimal representation of the percentage.
    """

    return percent / 10000

# Function to convert hectopascals to pascals
def convert_hpa_to_pa(pressure_hpa):
    """
    Convert pressure from hectopascals (hPa) to pascals (Pa).
    Args:
        pressure_hpa (float): Pressure in hectopascals (hPa).
    Returns:
        float: Pressure in pascals (Pa).
    """
    return pressure_hpa * 100

# Function to convert unixdata to iso8601
def convert_unix_time_to_iso8601(unix_timestamp):
    """
    Convert a Unix timestamp to an ISO 8601 formatted date string.
    Args:
        unix_timestamp (int): The Unix timestamp to convert.
    Returns:
        str: The converted date string in ISO 8601 format.
    """
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(unix_timestamp))

# Function to filter data
def extract_data(data):
    """
    Filters the input weather data dictionary to extract specific fields.
    Args:
        data (dict): A dictionary containing weather data with the following structure:
            {
                "coord": {"lon": float, "lat": float},
                "wind": {"speed": float, "deg": float},
                "main": {
                    "temp": float,
                    "sea_level": float,
                    "grnd_level": float,
                    # "humidity": int,  # Not implemented
                },
                "clouds": {"all": int},
                "rain": {"1h": float},  # Optional
                "snow": {"1h": float},  # Optional
                "dt": int,
                "timezone": int
    Returns:
        dict: A dictionary containing the filtered data with the following keys:
            - "lon": Longitude
            - "lat": Latitude
            - "wind_speed": Wind speed
            - "wind_deg": Wind direction in degrees
            - "temperature": Temperature
            - "sea_level_pressure": Sea level pressure
            - "suface_pressure": Surface pressure
            - "humidity": Humidity percentage      
            - "cloudiness": Cloudiness percentage
            - "rain": Rain volume for the last hour (default is 0 if not present)
            - "snow": Snow volume for the last hour (default is 0 if not present)
            - "time_unix_format": Time of data calculation in Unix format
            - "timezone": Timezone offset in seconds
    """

    filtered = {
                "lon": data["coord"]["lon"],
                "lat": data["coord"]["lat"],
                "wind_speed": data["wind"]["speed"],
                "wind_deg": data["wind"]["deg"],
                "temperature": data["main"]["temp"],
                "sea_level_pressure": data["main"]["sea_level"],
                "suface_pressure":  data["main"]["grnd_level"],
                "humidity": data["main"]["humidity"],
                "cloudiness": data["clouds"]["all"],
                "rain": data["rain"]["1h"] if "rain" in data else 0,
                "snow": data["snow"]["1h"] if "snow" in data else 0,
                "time_unix_format": data["dt"],
                "timezone": data["timezone"]
            }
    return filtered

# Function to normalize data
def normalize_data(filtered):
    """
    Normalize the filtered weather data into a ecmwf era5 reanalysis format .
    Args:
        filtered (dict): A dictionary containing the filtered weather data with the following keys:
            - "lon" (float): Longitude.
            - "lat" (float): Latitude.
            - "wind_speed" (float): Wind speed.
            - "wind_deg" (float): Wind direction in degrees.
            - "temperature" (float): Temperature.
            - "sea_level_pressure" (float): Sea level pressure in hPa.
            - "suface_pressure" (float): Surface pressure in hPa.
            - "q_level_1000" (int): Humidity percentage. 
            - "cloudiness" (float): Cloudiness percentage.
            - "rain" (float): Rainfall amount.
            - "snow" (float): Snowfall amount.
            - "time_unix_format" (int): Unix timestamp.
            - "timezone" (str): Timezone information.
    Returns:
        dict: A dictionary containing the normalized weather data with the following keys:
            - "lon" (float): Longitude.
            - "lat" (float): Latitude.
            - "wind_speed" (float): Wind speed.
            - "wind_deg" (float): Wind direction in degrees.
            - "2t" (float): Temperature.
            - "msl" (float): Sea level pressure in Pa.
            - "sp" (float): Surface pressure in Pa.
            - "q_level_1000" (float): Humidity percentage. 
            - "tcc" (float): Cloudiness as a decimal.
            - "tp" (float): Total precipitation. # rain + snow # non implemented in pipeline
            - "ssrd" (float): Solar radiation.
            - "date_unix" (int): Unix timestamp. [UTC]
            - "acquisition_timestamp" (str): Acquisition timestamp in ISO 8601 format.[UTC+Timezone]
    """

    normalized={
        "longitude": filtered["lon"],
        "latitude": filtered["lat"],
        "wind_speed": filtered["wind_speed"],
        "wind_deg": filtered["wind_deg"],
        "2t": filtered["temperature"],
        "msl": convert_hpa_to_pa(filtered["sea_level_pressure"]),
        "sp": convert_hpa_to_pa(filtered["suface_pressure"]),
        "humidity": filtered["humidity"],
        "tcc": convert_percent_to_decimal(filtered["cloudiness"]),
        "tp": total_precipitation(filtered["rain"], filtered["snow"]),
        "ssrd": calculate_solar_radiation(filtered["cloudiness"], filtered["lat"],
                                           unix_to_day_of_year(filtered["time_unix_format"],filtered["timezone"]),
                                           unix_to_local_time(filtered["time_unix_format"],filtered["timezone"])),
        "date_unix": filtered["time_unix_format"],
        "acquisition_timestamp": convert_unix_time_to_iso8601(filtered["time_unix_format"])
    }

    return normalized
