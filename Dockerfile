# ==========================================
# Stage 1: Builder (Compile dependencies)
# ==========================================
FROM python:3.11-slim-bookworm as builder

WORKDIR /app

# Install system dependencies required for build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# Stage 2: Runtime (Minimal secure image)
# ==========================================
FROM python:3.11-slim-bookworm as runtime

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies (e.g. curl for healthcheck if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . /app

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Gradio port
EXPOSE 7860

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME="0.0.0.0" \
    GRADIO_SERVER_PORT=7860

# Check validility (Optional healthcheck)
HEALTHCHECK CMD curl --fail http://localhost:7860/ || exit 1

# Command to run the application
CMD ["python", "guidebook/gradio_app.py", "--demo-name", "daily_seongsu"]
