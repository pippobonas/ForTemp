FROM openjdk:11-jdk-slim

# Install necessary packages
USER root
RUN apt-get update && apt-get install -y wget gnupg maven

# Install Kafka
RUN wget https://archive.apache.org/dist/kafka/3.9.0/kafka_2.13-3.9.0.tgz && \
    tar -xzf kafka_2.13-3.9.0.tgz && \
    mv kafka_2.13-3.9.0 /opt/kafka && \
    rm kafka_2.13-3.9.0.tgz

# Set environment variables for Kafka
ENV KAFKA_HOME=/opt/kafka
ENV PATH=$PATH:$KAFKA_HOME/bin

# Set the working directory
WORKDIR /app

# Copy the Maven project files
COPY pom.xml /app
COPY src /app/src
# Build the project
RUN mvn clean package

# Copy the application JAR file to the final location
RUN cp target/kafka-streams-warm-up-1.0-SNAPSHOT.jar /app/kafka-streams-warm-up.jar

# Copy the application properties file
COPY src/main/resources/application.properties /app/application.properties

# Command to run the application
CMD ["java", "-cp", "kafka-streams-warm-up.jar", "com.data_aggregation_stream.KafkaStreamsWarmUp"]