# Simple LibreOffice-based DOCX to PDF converter
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

# Copy application files
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

# Default command - run the API
CMD ["python", "src/main.py"]
