# Multi-stage production Dockerfile for Oatie AI Frontend
# ======================================================

# Build stage
FROM node:18-alpine as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG GIT_COMMIT
ARG REACT_APP_API_URL
ARG REACT_APP_ENVIRONMENT=production

# Set work directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production --silent

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Install additional packages
RUN apk add --no-cache curl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx user and set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Add labels for metadata
LABEL maintainer="Oatie AI Team" \
      version="${VERSION}" \
      description="Oatie AI Reporting Platform Frontend" \
      build-date="${BUILD_DATE}" \
      git-commit="${GIT_COMMIT}"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
