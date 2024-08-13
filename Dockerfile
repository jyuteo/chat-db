# -----------------------
# Frontend Stage
# -----------------------
FROM node:22-alpine AS frontend-build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# # -----------------------
# # Backend Stage
# # -----------------------
# FROM python:3.10-slim AS backend-build

# WORKDIR /app

# COPY backend/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY backend/ .

# -----------------------
# Final Stage
# -----------------------
FROM python:3.10-slim

# Install necessary packages for running Nginx and Redis
RUN apt-get update && apt-get install -y nginx redis-server supervisor && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ /app

# Copy frontend build to Nginx directory
COPY --from=frontend-build /app/dist /usr/share/nginx/html

# # Copy backend
# COPY --from=backend-build /app /app

# Copy Nginx and Supervisor configuration files
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY supervisor/supervisord.conf /etc/supervisord.conf

# Expose the single Heroku port
EXPOSE $PORT

# Start all services using Supervisor
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
