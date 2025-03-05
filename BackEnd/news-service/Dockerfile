# Use official Python image as base
FROM python:3.11-slim

# Create a non-root user and set permissions
RUN useradd --create-home appuser

# Set working directory
WORKDIR /app

# Switch to the new user before installing packages
USER appuser

# Ensure ~/.local/bin exists and set PATH
ENV PATH="/home/appuser/.local/bin:$PATH"

# Copy dependencies file
COPY --chown=appuser:appuser requirements.txt .

# Install dependencies in user-specific directory
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application files
COPY --chown=appuser:appuser app/ ./app

# Expose FastAPI port
EXPOSE ${APP_PORT:-8000}

# Set environment variables (optional, since .env is used)
ENV PYTHONUNBUFFERED=1

# Run Gunicorn with Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:${APP_PORT:-8000}", "app.main:app"]
