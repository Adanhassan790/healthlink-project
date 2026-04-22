# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with better error handling
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files (without requiring database)
RUN python manage.py collectstatic --noinput --clear || true

# Create a startup shell script directly
RUN echo '#!/bin/sh\n\
set -e\n\
echo "===================================================="\n\
echo "Starting Django Application..."\n\
echo "===================================================="\n\
echo ""\n\
echo "Step 1: Running Database Migrations..."\n\
python manage.py migrate --noinput\n\
echo ""\n\
echo "Step 2: Migrations Complete"\n\
echo "===================================================="\n\
echo "Step 3: Starting Gunicorn Server..."\n\
echo "===================================================="\n\
echo ""\n\
exec gunicorn \\\n\
  --bind 0.0.0.0:8000 \\\n\
  --workers 4 \\\n\
  --worker-class sync \\\n\
  --timeout 120 \\\n\
  --access-logfile - \\\n\
  --error-logfile - \\\n\
  healthlink.wsgi:application' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Use the shell script as entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
