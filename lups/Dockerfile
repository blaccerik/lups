# Use an official Node.js runtime as a parent image
FROM node:18-alpine as builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Install project dependencies
RUN npm install

# Copy the rest of your application's source code to the working directory
COPY . .

# Build your Angular application
RUN ng build

# Use Nginx as the base image for serving the Angular app
FROM nginx:alpine

# Install bash for debugging purposes
RUN apk update && apk add bash

COPY nginx.conf /etc/nginx/nginx.conf

# Copy the built Angular app from the previous stage into the Nginx directory
COPY --from=builder /app/dist/lups /usr/share/nginx/html

# Expose port 80 to the outside world
EXPOSE 80

# Start Nginx when the container runs
CMD ["nginx", "-g", "daemon off;"]
