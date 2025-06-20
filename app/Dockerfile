# Use a lightweight Python 3.9 base image
FROM python:3.9-slim

# Install security updates and required packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl gcc && \
    pip install --no-cache-dir --no-warn-script-location uvicorn && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
# -  The `--no-install-recommends` flag minimizes unnecessary packages.
# - `rm -rf /var/lib/apt/lists/*`: Removes apt cache to reduce image size.

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# The `--chown=appuser:appuser` flag sets ownership to the non-root user
COPY --chown=appuser:appuser . .

#`--no-warn-script-location` suppresses warnings about script locations.
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
