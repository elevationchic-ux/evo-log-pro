FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Alembic-managed deploy entrypoint (migrate then serve). Ensure it runs on
# LF/Unix line endings regardless of the build host.
RUN chmod +x docker-entrypoint.sh && sed -i 's/\r$//' docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Run migrations then start the application - PORT env var injected by Railway
CMD ["./docker-entrypoint.sh"]