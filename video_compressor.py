import os
import subprocess
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# Directories
INPUT_DIR = "obfuscated"
OUTPUT_DIR = "compressed"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compress_video(video_file):
    """Compress a single video file"""
    input_path = os.path.join(INPUT_DIR, video_file)
    output_path = os.path.join(OUTPUT_DIR, video_file)

    # Skip if already exists
    if os.path.exists(output_path):
        return f"Skipped: {video_file}"

    # Try GPU first, fallback to fast CPU encoding
    gpu_cmd = [
        'ffmpeg',
        '-hwaccel', 'cuda',
        '-i', input_path,
        '-c:v', 'h264_nvenc',
        '-preset', 'p4',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-y',
        output_path
    ]

    cpu_cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-y',
        output_path
    ]

    try:
        subprocess.run(gpu_cmd, check=True, capture_output=True)
        return f"Completed (GPU): {video_file}"
    except subprocess.CalledProcessError:
        # Try CPU fallback
        try:
            subprocess.run(cpu_cmd, check=True, capture_output=True)
            return f"Completed (CPU): {video_file}"
        except subprocess.CalledProcessError:
            return f"Error: {video_file}"

# Get all mp4 files
mp4_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.mp4')])

print(f"Found {len(mp4_files)} videos to compress")

# Use parallel processing with number of GPUs or CPUs
max_workers = min(4, multiprocessing.cpu_count())  # Adjust based on your GPUs

with ProcessPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(compress_video, video_file): video_file for video_file in mp4_files}

    for future in tqdm(as_completed(futures), total=len(mp4_files), desc="Compressing videos"):
        result = future.result()
        if "Error" in result:
            print(f"\n{result}")

print("Compression complete!")
