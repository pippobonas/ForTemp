#! venv/bin/python

import sys

from Module.Api_request_cds.send_request import iterate_download_response as idr
from Module.Csv_utils.Utils import all_grib_one_csv as agoc

if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 4:
        print("Usage: python main.py <Operation> <DIR output > <DIR input>")
        print("Operation: [download] [output.csv]")
        sys.exit(1)

    if sys.argv[1] == "download":
        idr(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "output.csv":
        agoc(sys.argv[3],sys.argv[2])
        