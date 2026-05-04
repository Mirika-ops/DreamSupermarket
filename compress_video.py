#!/usr/bin/env python3
"""
Ultra-lightweight video compression using OpenCV.
Reduces resolution and fps for web delivery.
"""
import os
import cv2

source_path = r"F:\研一\Tech Direction\合作项目\TD_26.mp4"
output_path = r"F:\研一\Tech Direction\tdspring26\tdspring26\public\videos\TD_26.mp4"

print(f"Loading video: {source_path}")
cap = cv2.VideoCapture(source_path)

if not cap.isOpened():
    print("Error: Could not open video file")
    exit(1)

# Get video properties
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Original - Duration: {total_frames/fps:.1f}s | Resolution: {width}x{height} | FPS: {fps}")

# Compression settings - ultra-aggressive for web
new_width = int(width * 0.4)  # Reduce width to 40%
new_height = int(height * 0.4)  # Reduce height to 40%
new_fps = 15  # Lower FPS for streaming
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

print(f"Compressing to {new_width}x{new_height} @ {new_fps}fps...")

writer = cv2.VideoWriter(output_path, fourcc, new_fps, (new_width, new_height))

frame_count = 0
skip_frames = max(1, int(fps / new_fps))  # Skip frames if reducing FPS

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Skip frames if needed
    if frame_count % skip_frames == 0:
        # Resize frame
        resized = cv2.resize(frame, (new_width, new_height))
        writer.write(resized)
    
    frame_count += 1
    if frame_count % 100 == 0:
        progress = (frame_count / total_frames) * 100
        print(f"Progress: {progress:.1f}%")

cap.release()
writer.release()

output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"\n✓ Video compressed successfully!")
print(f"Output: {output_path}")
print(f"Compressed size: {output_size_mb:.1f} MB")
