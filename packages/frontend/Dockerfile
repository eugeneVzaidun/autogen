# Use the official Nginx image from Docker Hub
FROM nginx:latest

# Remove the default Nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy your static website files from the dist folder to Nginx's html directory
COPY ./dist/packages/frontend /usr/share/nginx/html/

# (Optional) If you have a custom Nginx configuration, copy it
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 to the host
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]