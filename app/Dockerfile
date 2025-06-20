# Use a specific Python 3.9 version with security fixes
FROM python:3.9.19-slim-bookworm

# Install security updates and required packages with minimal footprint
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && pip install --no-cache-dir --no-warn-script-location --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --no-warn-script-location uvicorn && \
    apt-get purge -y --auto-remove gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python requirements with version pinning
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
