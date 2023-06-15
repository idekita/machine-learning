# Use an appropriate base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of application code
COPY . .

# Expose port 5000
EXPOSE 5000

# Set the entrypoint command
CMD [ "python", "app.py" ]
