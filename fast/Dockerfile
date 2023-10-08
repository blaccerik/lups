# Use the official Python image as the base image
FROM python:3.10.9-slim

# Set the working directory inside the container
WORKDIR /app

# postgre stuff
RUN apt-get update && apt-get -y install libpq-dev gcc

# Copy the requirements.txt file
COPY requirements.txt .

# Install any dependencies needed for your application
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY . .

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]