# Stage 1: Build environment
FROM node:18-alpine as builder
WORKDIR /app

# Copy package files FIRST (critical for caching)
COPY package.json package-lock.json ./

# Install dependencies using locked versions
RUN npm ci --silent

# Copy all other files
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production server
FROM nginx:1.23-alpine

# Copy build artifacts
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]