#!/bin/bash
# Build script for Render

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg
apt-get update
apt-get install -y ffmpeg

echo "Build completed successfully!"
