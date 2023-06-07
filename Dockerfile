# Use the official TensorFlow Serving Docker image as the base image
FROM tensorflow/serving

# Set the working directory inside the container
WORKDIR /app

# Copy the code and dependencies into the container
COPY . /app

# Expose the ports for gRPC and REST
EXPOSE 8500
EXPOSE 8501

# Set the model name and base path
ENV MODEL_NAME=recommendation
ENV MODEL_BASE_PATH=/app

# Start TensorFlow Serving when the container launches
CMD ["tensorflow_model_server", "--port=8500", "--rest_api_port=8501", "--model_name=${MODEL_NAME}", "--model_base_path=${MODEL_BASE_PATH}"]
