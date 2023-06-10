# Use the official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code to the container
COPY . .

# Expose the required port
EXPOSE 5500

# Run the Flask application
CMD ["python", "app.py"]
