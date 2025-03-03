# Use official Python image as base
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app

# Expose FastAPI port
EXPOSE 8000

# Set environment variables (optional, since .env is used)
ENV PYTHONUNBUFFERED=1

# Command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
