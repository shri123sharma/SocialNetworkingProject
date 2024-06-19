# Dockerfile

# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Apply migrations and collect static files (if any)
RUN python manage.py migrate


# Define the command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
