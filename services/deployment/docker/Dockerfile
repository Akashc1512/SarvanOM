# Multi-stage Dockerfile for Universal Knowledge Platform
# Production-ready containerization with security and optimization

# Stage 1: Base Python image with security updates
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        wget \
        gnupg \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Stage 2: Dependencies installation
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Development dependencies (for testing)
FROM dependencies as dev-dependencies

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Stage 4: Application build
FROM dependencies as build

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache

# Set proper permissions
RUN chown -R appuser:appuser /app

# Stage 5: Production image
FROM base as production

# Set working directory
WORKDIR /app

# Copy Python dependencies from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=build /app /app

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache /app/tmp

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 6: Development image
FROM dev-dependencies as development

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache /app/tmp

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Default command for development
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 7: Testing image
FROM dev-dependencies as testing

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/cache /app/tmp

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Default command for testing
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=services", "--cov-report=html"]

# Stage 8: Security scanning
FROM production as security-scan

# Install security scanning tools
RUN pip install --no-cache-dir bandit safety

# Run security scans
RUN bandit -r /app -f json -o /tmp/bandit-report.json || true
RUN safety check --json --output /tmp/safety-report.json || true

# Stage 9: Final production image
FROM production as final

# Copy security scan results if needed
COPY --from=security-scan /tmp/*.json /app/security-reports/

# Add labels for better container management
LABEL maintainer="Universal Knowledge Platform Team" \
      version="2.4.0" \
      description="Universal Knowledge Platform - Production Container" \
      org.opencontainers.image.source="https://github.com/your-org/universal-knowledge-platform"

# Final health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 