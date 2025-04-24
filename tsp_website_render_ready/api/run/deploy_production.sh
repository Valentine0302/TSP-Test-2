#!/bin/bash

# Sea Freight Calculator Production Deployment Script
# This script sets up and deploys the Sea Freight Calculator to production

# Exit on error
set -e

echo "Starting Sea Freight Calculator deployment..."

# Create necessary directories
mkdir -p /var/www/sea_freight_calculator
mkdir -p /var/log/sea_freight_calculator
mkdir -p /etc/sea_freight_calculator

# Install required packages
echo "Installing required packages..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx supervisor

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv /var/www/sea_freight_calculator/venv
source /var/www/sea_freight_calculator/venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install flask flask-cors gunicorn requests

# Copy application files
echo "Copying application files..."
cp -r ./api/run/* /var/www/sea_freight_calculator/
cp -r ./frontend/* /var/www/sea_freight_calculator/static/

# Create .env file for API keys
echo "Creating environment configuration..."
cat > /etc/sea_freight_calculator/.env << EOF
# API Keys for shipping services
SEARATES_API_KEY=your_searates_api_key
FREIGHTOS_API_KEY=your_freightos_api_key
WORLDFREIGHTRATES_API_KEY=your_worldfreightrates_api_key

# Database configuration
DB_PATH=/var/www/sea_freight_calculator/sea_freight.db

# Email configuration
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
EMAIL_FROM=noreply@example.com
EOF

# Create WSGI entry point
echo "Creating WSGI entry point..."
cat > /var/www/sea_freight_calculator/wsgi.py << EOF
import os
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/etc/sea_freight_calculator/.env')

# Add application directory to path
sys.path.insert(0, '/var/www/sea_freight_calculator')

# Import the Flask application
from sea_freight_api import app as application

if __name__ == "__main__":
    application.run()
EOF

# Configure Nginx
echo "Configuring Nginx..."
cat > /etc/nginx/sites-available/sea_freight_calculator << EOF
server {
    listen 80;
    server_name sea-freight.example.com;

    location /static {
        alias /var/www/sea_freight_calculator/static;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    access_log /var/log/nginx/sea_freight_access.log;
    error_log /var/log/nginx/sea_freight_error.log;
}
EOF

# Enable the Nginx site
ln -sf /etc/nginx/sites-available/sea_freight_calculator /etc/nginx/sites-enabled/

# Configure Supervisor
echo "Configuring Supervisor..."
cat > /etc/supervisor/conf.d/sea_freight_calculator.conf << EOF
[program:sea_freight_calculator]
directory=/var/www/sea_freight_calculator
command=/var/www/sea_freight_calculator/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/sea_freight_calculator/gunicorn.err.log
stdout_logfile=/var/log/sea_freight_calculator/gunicorn.out.log
user=www-data
group=www-data
environment=PYTHONPATH="/var/www/sea_freight_calculator"
EOF

# Set proper permissions
echo "Setting permissions..."
chown -R www-data:www-data /var/www/sea_freight_calculator
chown -R www-data:www-data /var/log/sea_freight_calculator
chmod 750 /etc/sea_freight_calculator/.env

# Restart services
echo "Restarting services..."
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl restart sea_freight_calculator

echo "Sea Freight Calculator deployment completed successfully!"
echo "Please update the API keys in /etc/sea_freight_calculator/.env with your actual keys."
echo "Your application should be available at: http://sea-freight.example.com"
