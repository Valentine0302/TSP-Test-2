#!/bin/bash
# Build script for Render.com deployment

# Create necessary directories
mkdir -p api/run/static

# Copy static files to the correct location
cp -r css js images calculation index.html api/run/static/

# Make sure the database directory exists
mkdir -p api/run/data

# Initialize the database if needed
python api/run/db_schema.py

# Print completion message
echo "Build completed successfully"
