# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 6030 available to the world outside this container
EXPOSE 6030

# Define environment variables for Flask and Gunicorn
ENV FLASK_APP=run.py
ENV FLASK_CONFIG=production

# Run the application using Gunicorn
# Using run:app because run.py creates the 'app' instance
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:6030", "run:app"]