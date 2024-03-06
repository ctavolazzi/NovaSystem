# Use the official lightweight Node.js 16 image.
# https://hub.docker.com/_/node
FROM node:16-slim

# Create and change to the app directory.
WORKDIR /Users/ctavolazzi/Code/NovaSystem/novasystem-svelte-docker

# Copy application dependency manifests to the container image.
# A wildcard is used to ensure both package.json AND package-lock.json are copied.
# Copying this separately prevents re-running npm install on every code change.
COPY package*.json ./

# Install production dependencies.
RUN npm install --frozen-lockfile

# Copy local code to the container image.
COPY . .

# Build the Svelte app.
RUN npm run build

EXPOSE 8080

ENV HOST=0.0.0.0

# Run the web service on container startup.

# Start the Svelte development server on all interfaces
CMD ["npm", "run", "dev", "--", "--host", "localhost", "--port", "8080"]



