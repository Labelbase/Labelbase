# Use official nginx image with explicit platform support
FROM --platform=$BUILDPLATFORM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 8080
EXPOSE 8080

# Use the default nginx entrypoint
CMD ["nginx", "-g", "daemon off;"]
