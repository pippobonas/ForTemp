FROM python:alpine3.20

# Install pip and dcron
RUN apk update && apk add --no-cache python3 py3-pip dcron

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install them
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Copy the application code
COPY . /app

# Add crontab file in the cron directory
ADD ./data/crontab /etc/crontabs/root

# Give execution rights on the cron job
RUN chmod 0644 /etc/crontabs/root

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD ["sh", "-c", "crond -f -l 2 & tail -f /var/log/cron.log"]


