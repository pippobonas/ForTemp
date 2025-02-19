FROM python:3.11-bookworm

# Update and upgrade the system packages
RUN apt-get update && \
    apt-get upgrade -y 
RUN apt-get install -y --no-install-recommends cdo

WORKDIR /
VOLUME [ "/data" ]
ENV OUTPUT_DIR="/data"

COPY Api_request_cds /Api_request_cds/
COPY Convert_grib_in_csv /Convert_grib_in_csv/

RUN pip install --upgrade pip && \
    pip install -r /Api_request_cds/requirements.txt && \
    pip install -r /Convert_grib_in_csv/requirements.txt

CMD python /Api_request_cds/send_request.py && \
    ./Convert_grib_in_csv/convert_grib_to_csv.py $OUTPUT_DIR $OUTPUT_DIR
