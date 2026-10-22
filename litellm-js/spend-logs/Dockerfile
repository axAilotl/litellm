# Use the specific Node.js v20.11.0 image
FROM node:22.23.4-alpine@sha256:fe4f6d74e20370acb04ad889077d14d0f64a9c8ea6a42bc60cddf1e844699914

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY ./litellm-js/spend-logs/package*.json ./

# Install dependencies
RUN npm install

# Install Prisma globally
RUN npm install -g prisma

# Copy the rest of the application code
COPY ./litellm-js/spend-logs .

# Generate Prisma client
RUN npx prisma generate

# Expose the port that the Node.js server will run on
EXPOSE 3000

# Command to run the Node.js app with npm run dev
CMD ["npm", "run", "dev"]
