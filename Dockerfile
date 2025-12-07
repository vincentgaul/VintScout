# Multi-stage Dockerfile for VintedScanner Web
#
# This file tells Docker how to package our application into a container.
# A container is like a lightweight virtual machine that includes everything
# needed to run the app (code, dependencies, runtime environment).
#
# We use a "multi-stage build" which means:
# Stage 1: Build the React frontend (turns JSX/TypeScript into HTML/CSS/JS)
# Stage 2: Set up Python backend and copy in the built frontend
#
# Why multi-stage? To keep the final container small - we don't need Node.js
# in the final image, only the built frontend files.
#
# To build: docker build -t vintedscanner-web .
# To run: docker-compose up

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Backend with frontend assets
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source (excluding data directory)
COPY backend/ ./backend/

# Copy frontend build from previous stage
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Make startup script executable
RUN chmod +x /app/backend/startup.sh

# Create data directory for SQLite (user data will go here)
RUN mkdir -p /app/backend/data

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:3000/health')"

# Run startup script
CMD ["/app/backend/startup.sh"]
