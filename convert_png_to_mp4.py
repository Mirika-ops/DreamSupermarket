#!/usr/bin/env python3
"""
Convert PNG frame sequences to MP4 videos using OpenCV (cv2)
No FFmpeg dependency required - uses codec directly
"""

from pathlib import Path
import cv2
import numpy as np

VIDEOS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\videos")
FPS = 24

def log(message, level="INFO"):
    """Print log message."""
    print(f"[{level}] {message}")

def get_image_dimensions(image_path):
    """Get image dimensions."""
    img = cv2.imread(str(image_path))
    if img is not None:
        return img.shape[1], img.shape[0], img.shape[2]  # width, height, channels
    return None, None, None

def convert_frames_to_mp4_cv2(frames_dir, output_mp4, fps=24):
    """Convert PNG frame sequence to MP4 using OpenCV."""
    
    if not frames_dir.exists():
        log(f"✗ Frames directory not found: {frames_dir}", "ERROR")
        return False
    
    frames = sorted(list(frames_dir.glob("frame_*.png")))
    if not frames:
        log(f"✗ No PNG frames found in {frames_dir.name}", "ERROR")
        return False
    
    log(f"  Converting {len(frames)} frames...")
    
    try:
        # Get frame dimensions from first frame
        width, height, channels = get_image_dimensions(frames[0])
        if width is None:
            log(f"✗ Cannot read first frame", "ERROR")
            return False
        
        log(f"  Frame size: {width}x{height}, Frames: {len(frames)}")
        
        # Create video writer
        # Try H.264 codec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # H.264/MPEG-4
        out = cv2.VideoWriter(str(output_mp4), fourcc, fps, (width, height))
        
        if not out.isOpened():
            log(f"✗ Failed to open video writer", "ERROR")
            return False
        
        # Write frames
        for i, frame_path in enumerate(frames, 1):
            frame = cv2.imread(str(frame_path))
            if frame is None:
                log(f"✗ Cannot read frame: {frame_path.name}", "ERROR")
                continue
            
            out.write(frame)
            
            if i % 50 == 0:
                progress = (i / len(frames)) * 100
                log(f"    Progress: {i}/{len(frames)} ({progress:.0f}%)")
        
        out.release()
        
        if output_mp4.exists():
            file_size_mb = output_mp4.stat().st_size / (1024 * 1024)
            log(f"  ✓ Created: {output_mp4.name} ({file_size_mb:.1f} MB)", "SUCCESS")
            return True
        else:
            log(f"✗ Output file not created", "ERROR")
            return False
            
    except Exception as e:
        log(f"✗ Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main conversion process."""
    log("=" * 70)
    log("PNG SEQUENCE TO MP4 CONVERTER (OpenCV)", "HEADER")
    log("=" * 70)
    
    if not VIDEOS_PATH.exists():
        log(f"✗ Videos path not found: {VIDEOS_PATH}", "ERROR")
        return
    
    # Find all *_frames directories
    frame_dirs = sorted([d for d in VIDEOS_PATH.glob("*_frames") if d.is_dir()])
    
    if not frame_dirs:
        log("✗ No frame directories found", "ERROR")
        return
    
    log(f"\nFound {len(frame_dirs)} frame sequences\n")
    
    converted_count = 0
    failed_count = 0
    skipped_count = 0
    
    for i, frames_dir in enumerate(frame_dirs, 1):
        log(f"\n[{i}/{len(frame_dirs)}] {frames_dir.name}")
        
        # Output MP4 beside the frames directory
        output_mp4 = VIDEOS_PATH / f"{frames_dir.name.replace('_frames', '')}.mp4"
        
        # Skip if MP4 already exists
        if output_mp4.exists():
            file_size_mb = output_mp4.stat().st_size / (1024 * 1024)
            log(f"  ⊘ Already exists ({file_size_mb:.1f} MB)")
            skipped_count += 1
            continue
        
        if convert_frames_to_mp4_cv2(frames_dir, output_mp4, FPS):
            converted_count += 1
        else:
            failed_count += 1
    
    log("\n" + "=" * 70)
    log(f"✓ CONVERSION COMPLETE", "HEADER")
    log(f"  Converted: {converted_count}")
    log(f"  Skipped: {skipped_count}")
    log(f"  Failed: {failed_count}")
    log(f"  Output: {VIDEOS_PATH}")
    log("=" * 70)

if __name__ == "__main__":
    main()
