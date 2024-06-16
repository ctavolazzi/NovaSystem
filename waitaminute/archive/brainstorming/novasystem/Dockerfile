# Use the official Node.js image as a parent image
FROM node:18

# Set the working directory in the Docker image
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install any dependencies
RUN npm install

# Copy the rest of your source code to the Docker image
COPY . .

# Expose the port that SvelteKit will run on
EXPOSE 3000

# Run the SvelteKit application in development mode using vite directly
CMD ["npx", "vite"]


