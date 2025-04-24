#!/bin/bash
# Build script for Render.com deployment

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p api/run/static

# Copy static files to the correct location
cp -r css js images calculation index.html api/run/static/

# Print directory contents for debugging
echo "Содержимое директории api/run/static:"
ls -la api/run/static/

# Print completion message
echo "Build completed successfully"
