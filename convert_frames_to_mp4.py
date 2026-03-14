#!/usr/bin/env python3
"""
Convert PNG frame sequences to MP4 videos using FFmpeg
"""

from pathlib import Path
import subprocess
import sys

VIDEOS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\videos")
FPS = 24

def log(message, level="INFO"):
    """Print log message."""
    print(f"[{level}] {message}")

def convert_frames_to_mp4(frames_dir, output_mp4, fps=24):
    """Convert PNG frame sequence to MP4 using FFmpeg."""
    
    if not frames_dir.exists():
        log(f"✗ Frames directory not found: {frames_dir}", "ERROR")
        return False
    
    frames = sorted(list(frames_dir.glob("frame_*.png")))
    if not frames:
        log(f"✗ No PNG frames found in {frames_dir.name}", "ERROR")
        return False
    
    log(f"Converting {len(frames)} frames to MP4...")
    
    # FFmpeg command: pattern-based input from PNG sequence
    frame_pattern = str(frames_dir / "frame_%04d.png")
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-framerate", str(fps),
        "-i", frame_pattern,
        "-c:v", "libx264",
        "-preset", "fast",           # fast encoding
        "-crf", "23",                # quality (18-28, lower=better)
        "-pix_fmt", "yuv420p",       # compatibility
        "-y",                        # overwrite output
        str(output_mp4)
    ]
    
    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            log(f"FFmpeg error: {result.stderr}", "ERROR")
            return False
        
        if output_mp4.exists():
            file_size_mb = output_mp4.stat().st_size / (1024 * 1024)
            log(f"✓ Created: {output_mp4.name} ({file_size_mb:.1f} MB)", "SUCCESS")
            return True
        else:
            log(f"✗ Output file not created", "ERROR")
            return False
            
    except FileNotFoundError:
        log("✗ FFmpeg not found. Install with: choco install ffmpeg -y", "ERROR")
        return False
    except subprocess.TimeoutExpired:
        log("✗ Conversion timeout", "ERROR")
        return False
    except Exception as e:
        log(f"✗ Error: {e}", "ERROR")
        return False

def main():
    """Main conversion process."""
    log("=" * 70)
    log("PNG SEQUENCE TO MP4 CONVERTER", "HEADER")
    log("=" * 70)
    
    if not VIDEOS_PATH.exists():
        log(f"✗ Videos path not found: {VIDEOS_PATH}", "ERROR")
        return
    
    # Find all *_frames directories
    frame_dirs = sorted([d for d in VIDEOS_PATH.glob("*_frames") if d.is_dir()])
    
    if not frame_dirs:
        log("✗ No frame directories found", "ERROR")
        return
    
    log(f"\nFound {len(frame_dirs)} frame sequences:\n")
    
    converted_count = 0
    failed_count = 0
    
    for i, frames_dir in enumerate(frame_dirs, 1):
        log(f"[{i}/{len(frame_dirs)}] {frames_dir.name}")
        
        # Output MP4 beside the frames directory
        output_mp4 = VIDEOS_PATH / f"{frames_dir.name.replace('_frames', '')}.mp4"
        
        # Skip if MP4 already exists
        if output_mp4.exists():
            file_size_mb = output_mp4.stat().st_size / (1024 * 1024)
            log(f"  ⊘ Already exists ({file_size_mb:.1f} MB)")
            continue
        
        if convert_frames_to_mp4(frames_dir, output_mp4, FPS):
            converted_count += 1
        else:
            failed_count += 1
        
        log("")
    
    log("=" * 70)
    log(f"✓ CONVERSION COMPLETE", "HEADER")
    log(f"  Converted: {converted_count}")
    log(f"  Failed: {failed_count}")
    log(f"  Output: {VIDEOS_PATH}")
    log("=" * 70)

if __name__ == "__main__":
    main()
