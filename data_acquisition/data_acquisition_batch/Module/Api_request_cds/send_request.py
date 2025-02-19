import json
import cdsapi
import os

"""
This module provides functions to send requests to the CDS API and download the response.

Functions:
- get_request(file_path): Reads a JSON request from a file and returns it as a dictionary.
- download_response(request, out_dir=None): Sends a request to the CDS API and downloads the response to the specified output directory.
"""

'''
    Reads a JSON request from a file and returns it as a dictionary.

    Args:
        file_path (str): The path to the JSON file containing the request.

    Returns:
        dict: The request data as a dictionary.
    pass
'''
def get_request(file_path):
    with open(file_path) as req:
        request = json.load(req)
    return request

def iterate_request_dir(dir_path):
    requests = []
    for file in os.listdir(dir_path):
        if file.endswith(".json"):
            requests.append(get_request(os.path.join(dir_path, file)))
    return requests

def get_script_dir():
        return os.path.dirname(os.path.realpath(__file__))

'''
    Sends a request to the CDS API and downloads the response to the specified output directory.

    Args:
        request (dict): The request data as a dictionary.
        out_dir (str, optional): The directory where the response will be saved. Defaults to "data".

    Returns:
        None
'''
def download_response(request, out_dir=None):
    cds = cdsapi.Client()
    if out_dir is None:
        out_dir = os.path.join(get_script_dir(), "data")
        
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, request.get("filename")), exist_ok=True)

    print("Variable:", request.get("variable"))
    print("Output Directory:", out_dir)
    print("Output File Path:", os.path.join(out_dir, request.get("filename"), request.get("filename")+".grib"))

    cds.retrieve(
        request.get("variable"),
        request.get("options"),
        os.path.join(out_dir , request.get("filename"),request.get("filename") + ".grib" ),
    )

    print("File downloaded successfully")


'''
    Iterates over all JSON request files in the specified directory, sends each request to the CDS API, and downloads the response to the specified output directory.
    Args:
        out_dir (str, optional): The directory where the responses will be saved. Defaults to "data".
        dir_path (str, optional): The directory containing the JSON request files. Defaults to a "request" directory in the script's directory.
    Returns:
        list: A list of request dictionaries that were processed.
'''
def iterate_download_response(out_dir=None,dir_path=os.path.join(get_script_dir(), "request")):
    requests = iterate_request_dir(dir_path)
    for request in requests:
        download_response(request, out_dir)
    return requests


