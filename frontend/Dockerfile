# Frontend Dockerfile for SarvanOM
# Optimized for Windows 11 Docker Desktop with WSL2 backend

# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --omit=dev

# Copy source code
COPY . .

# Create .env.local for Docker environment
RUN echo "NEXT_PUBLIC_API_BASE_URL=http://sarvanom_backend:8000" > .env.local && \
    echo "VITE_API_BASE_URL=http://sarvanom_backend:8000" >> .env.local

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start development server
CMD ["npm", "run", "dev"] 