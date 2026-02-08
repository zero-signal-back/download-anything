#!/bin/bash
# Build script for Render

# Install Python dependencies
pip install -r requirements.txt

# Install static FFmpeg binary
python -c "from static_ffmpeg import run; run.add_paths()"

echo "Build completed successfully!"
