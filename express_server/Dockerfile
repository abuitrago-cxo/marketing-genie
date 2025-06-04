# Stage 1: Build React Frontend (copied from main Dockerfile for self-containment if needed,
# but ideally frontend is built before and 'dist' is copied)
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the frontend
RUN npm run build

# Stage 2: Node.js Express Server
FROM node:20-alpine

WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY express_server/package*.json ./express_server/
RUN cd express_server && npm install

# Bundle app source
COPY express_server/ ./express_server/

# Copy built frontend from the frontend-builder stage
# The Node.js server expects it at ../frontend/dist relative to express_server/server.js
# So if server.js is at /usr/src/app/express_server/server.js,
# then ../frontend/dist needs to be /usr/src/app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Define environment variable for the port (optional, server.js already handles this)
ENV PORT=3000
ENV PYTHON_BACKEND_URL="http://127.0.0.1:8000" # Default, will be overridden by docker-compose

WORKDIR /usr/src/app/express_server
CMD [ "node", "server.js" ]
