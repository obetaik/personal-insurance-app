FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Added this when health check for backend was failing even
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*


# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /app/uploads/documents /app/uploads/temp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
# ENV FLASK_ENV=production


# Expose port
EXPOSE 4000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:4000",  "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]