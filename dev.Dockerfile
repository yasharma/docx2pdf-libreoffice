# Development LibreOffice-based DOCX to PDF converter with FastAPI dev mode
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install LibreOffice and fonts
RUN apt-get update && apt-get install -y \
    curl \
    default-jre-headless \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto \
    libreoffice \
    libreoffice-java-common \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (in dev mode, src will be mounted as volume)
COPY src/ /app/src/

# Create user and directories with proper permissions
RUN useradd -r -m -s /bin/bash dockeruser && \
    mkdir -p /app/input /app/output && \
    mkdir -p /home/dockeruser/.config/libreoffice/4/user && \
    mkdir -p /home/dockeruser/.cache && \
    chown -R dockeruser:dockeruser /app /home/dockeruser

USER dockeruser

# Set environment variables for LibreOffice
ENV HOME=/home/dockeruser
ENV SAL_USE_VCLPLUGIN=svp
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PYTHONPATH=/app

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthcheck || exit 1

# Default command - run FastAPI in development mode with auto-reload using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
