#!/bin/bash

# Run Playwright test with video recording
echo "Running Playwright test..."
npx playwright test all_phases_comprehensive.spec.ts --headed=false

# Find the most recent video file
VIDEO_DIR="test-results"
LATEST_VIDEO=$(find "$VIDEO_DIR" -name "*.webm" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")

if [ -z "$LATEST_VIDEO" ]; then
    echo "No video file found in $VIDEO_DIR"
    exit 1
fi

echo "Found video: $LATEST_VIDEO"

# Convert webm to mp4 using ffmpeg
OUTPUT_FILE="${LATEST_VIDEO%.webm}.mp4"
echo "Converting to mp4: $OUTPUT_FILE"

if command -v ffmpeg &> /dev/null; then
    ffmpeg -i "$LATEST_VIDEO" -c:v libx264 -c:a aac "$OUTPUT_FILE"
    echo "Conversion complete: $OUTPUT_FILE"
else
    echo "ffmpeg not found. Please install ffmpeg to convert videos."
    echo "Video saved as webm: $LATEST_VIDEO"
fi
