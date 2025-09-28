import os
import subprocess
import sys
from typing import Optional

def download_video(url: str, output_dir: str = "downloads", quality: str = "best") -> bool:
    """
    Download video from URL using yt-dlp

    Args:
        url: Video URL to download
        output_dir: Directory to save the video
        quality: Video quality preference (default: "best")

    Returns:
        bool: True if download successful, False otherwise
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Construct yt-dlp command
    cmd = [
        "yt-dlp",
        "-f", quality,
        "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
        url
    ]

    try:
        # Execute yt-dlp command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Successfully downloaded: {url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {url}: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: yt-dlp not found. Please install it with: pip install yt-dlp")
        return False

def download_video_segment(url: str, start_time: float, duration: float,
                          output_path: str, fps: int = 25) -> bool:
    """
    Download specific segment of video using yt-dlp + ffmpeg (inspired by ovr_downloader.py)

    Args:
        url: Video URL
        start_time: Start time in seconds
        duration: Duration in seconds
        output_path: Output file path
        fps: Frames per second

    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Construct command similar to ovr_downloader.py
        cmd = (f"ffmpeg -y -ss {start_time} "
               f"-i $(yt-dlp -f 18 --get-url {url}) "
               f"-t {duration} -c:v libx264 -r {fps} -vsync 0 {output_path}")

        result = os.system(cmd)
        if result == 0:
            print(f"Successfully downloaded segment: {output_path}")
            return True
        else:
            print(f"Error downloading segment from {url}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_downloader.py <video_url> [output_dir]")
        sys.exit(1)
    
    video_url = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else "downloads"
    
    success = download_video(video_url, output_directory)
    if not success:
        sys.exit(1)