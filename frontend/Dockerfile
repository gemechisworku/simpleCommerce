# Development Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clean install dependencies with legacy peer deps
RUN npm cache clean --force && \
    npm install --legacy-peer-deps

# Copy application code
COPY . .

# Expose port (must match PORT in docker-compose for dev)
EXPOSE 3001

# Set environment variable for React Scripts
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Start development server
CMD ["npm", "start"]

