FROM node:18-alpine as builder

WORKDIR /app

COPY lups/package*.json ./

RUN npm install

COPY lups/. .

RUN npm run ng build


FROM node:18-alpine as music_builder

WORKDIR /app

COPY music/package*.json ./

RUN npm install

COPY music/. .

RUN npm run ng build

# Use Nginx as the base image for serving the Angular app
FROM nginx:alpine

# Install bash for debugging purposes
RUN apk update && apk add bash

# Copy conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the built Angular app from the previous stage into the Nginx directory
COPY --from=builder /app/dist/lups/browser /var/www/html

COPY --from=music_builder /app/dist/music/browser /var/music/html

# Start Nginx when the container runs
CMD ["nginx", "-g", "daemon off;"]