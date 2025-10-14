# Multi-stage Dockerfile for TraderAgent
# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd --gid 1000 trader && \
    useradd --uid 1000 --gid trader --shell /bin/bash --create-home trader

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=trader:trader src/ ./src/
COPY --chown=trader:trader main.py .
COPY --chown=trader:trader demo_volume.py .

# Create data directory with proper permissions
RUN mkdir -p data && chown -R trader:trader /app

# Copy default balance files
COPY --chown=trader:trader data/balance.json ./data/
COPY --chown=trader:trader data/paper_balance.json ./data/

# Switch to non-root user
USER trader

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "main.py", "--live", "--paper"]