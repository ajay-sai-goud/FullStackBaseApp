# Frontend Dockerfile - React Application
# Simple single-stage build using serve package

# Use Node.js Alpine image for smaller size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# Use --legacy-peer-deps to resolve TypeScript version conflict with react-scripts
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build the React application
# Note: REACT_APP_API_BASE_URL can be set via build args or environment variables
ARG REACT_APP_API_BASE_URL=http://localhost:8000
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

RUN npm run build

# Install serve package globally to serve static files
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Serve the built application
CMD ["serve", "-s", "build", "-l", "3000"]

