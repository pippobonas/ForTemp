"""
This module provides utilities for extracting data from GRIB files, saving the data to CSV files, and performing
various operations on the data.
Functions:
    extract_grib_data(file_path, data_dict={}) -> dict:
        Extracts data from a GRIB file and stores it in a dictionary.
    save_dict_to_csv(data_dict, output_csv_path, name_file="output"):
        Saves a dictionary of data to a CSV file.
    save_csv(df, output_csv_path, name_file="output"):
        Saves a pandas DataFrame to a CSV file.
    list_extension_files_recursive(dir, extension) -> list:
        Returns a list of all files with a specific extension in a directory and its subdirectories.
    all_grib_one_csv(input_dir, output_csv_path):
        Extracts data from all GRIB files in a directory and saves it to a single CSV file.
"""
import eccodes
import pandas as pd
import datetime
import os
import sys

def extract_grib_data(file_path, data_dict={}):
    """
    Extracts data from a GRIB file and stores it in a dictionary.
    Args:
        file_path (str): The path to the GRIB file.
        data_dict (dict, optional): A dictionary to store the extracted data. Defaults to {}.
    Returns:
        dict: A dictionary containing the extracted data.
    """
    # Open the GRIB file
    with open(file_path, 'rb') as f:
        # Iterate over all messages in the GRIB file
        while True:
            try:
                # Read a new message from the file
                msg_id = eccodes.codes_grib_new_from_file(f)

                # Exit the loop if there are no more messages
                if msg_id is None:
                    break
                
                # Extract key information
                short_name = eccodes.codes_get(msg_id, 'shortName')
                level = eccodes.codes_get(msg_id, 'level') if eccodes.codes_is_defined(msg_id, 'level') else None
                data_date = eccodes.codes_get(msg_id,'dataDate')
                data_time = eccodes.codes_get(msg_id, 'dataTime')
                step_range = eccodes.codes_get(msg_id, 'stepRange')

                # Handle the case where step_range is a range
                step_range = step_range.split('-')[1] if '-' in step_range else step_range

                # Calculate the exact time
                # Convert data_date and data_time to datetime format
                date_str = f"{data_date} {data_time:04}"
                date_obj = datetime.datetime.strptime(date_str, "%Y%m%d %H%M")

                # Add step_range in hours
                exact_time = date_obj + datetime.timedelta(hours=int(step_range)+1)

                # Convert to Unix timestamp
                exact_time_unix = int(exact_time.timestamp())

                lats = eccodes.codes_get_array(msg_id, 'latitudes')
                lons = eccodes.codes_get_array(msg_id, 'longitudes')
                values = eccodes.codes_get_array(msg_id, 'values')

                # Add the data to the organized dictionary
                for i in range(len(values)):
                    key = (exact_time, lats[i], lons[i])  # Grouping by exact time, latitude, longitude

                    # Initialize the key if it does not exist
                    if key not in data_dict:
                        data_dict[key] = {'date_unix': exact_time_unix, 'latitude': lats[i], 'longitude': lons[i]}

                    # Add the variable value with its name
                    variable_name = f"{short_name}_level_{level}" if level else short_name
                    data_dict[key][variable_name] = values[i]
                # Release the message
                eccodes.codes_release(msg_id)

            except eccodes.CodesInternalError:
                # Exit the loop in case of error
                break
    return data_dict

def save_dict_to_csv(data_dict, output_csv_path, name_file="output"):
    """
    Saves a dictionary of data to a CSV file.
    Args:
        data_dict (dict): The dictionary containing the data to save.
        output_csv_path (str): The path to the output CSV file.
        name_file (str, optional): The name of the output CSV file. Defaults to "output".
    """
    # Convert the dictionary to a pandas DataFrame
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    # Save the DataFrame to a CSV file
    
    df = df.sort_values(by=['date_unix'])
    df.to_csv(os.path.join(output_csv_path,name_file+".csv"), index=False)

    print(f"Data saved in {output_csv_path}")

def save_csv(df, output_csv_path, name_file="output"):
    """
    Saves a pandas DataFrame to a CSV file.
    Args:
        df (pandas.DataFrame): The DataFrame containing the data to save.
        output_csv_path (str): The path to the output CSV file.
        name_file (str, optional): The name of the output CSV file. Defaults to "output".
    """
    # Save the DataFrame to a CSV file
    df.to_csv(os.path.join(output_csv_path,name_file+".csv"), index=False)
    df = df.sort_values(by=['date_unix'])
    print(f"Data saved in {output_csv_path}")

def list_extension_files_recursive(dir, extension):
    """
    Returns a list of all files with a specific extension in a directory and its subdirectories.
    Args:
        dir (str): The directory to search.
        extension (str): The file extension to search for.
    Returns:
        list: A list of file paths with the specified extension.
    """
    # Return all files with a specific extension in a directory and its subdirectories
    files = []
    for root, _, f in os.walk(dir):
        for file in f:
            if file.endswith(extension):
                files.append(os.path.join(root, file))
    return files

def all_grib_one_csv(input_dir, output_csv_path):
    """
    Extracts data from all GRIB files in a directory and saves it to a single CSV file.
    Args:
        input_dir (str): The directory containing the GRIB files.
        output_csv_path (str): The path to the output CSV file.
    """  
    data_dict = {}
    for file in list_extension_files_recursive(input_dir,'.grib'):
        extract_grib_data(file, data_dict)

    save_dict_to_csv(data_dict, output_csv_path)

