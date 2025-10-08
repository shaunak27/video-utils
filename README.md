
# Video Utils

This repository contains Python utilities for video processing, compression, downloading, and AI inference.

## Scripts

- `youtube_downloader.py`: Download full videos or specific segments from YouTube using `yt-dlp` and `ffmpeg`.
- `video_compressor.py`: Bulk compress videos in the `obfuscated/` folder to `compressed/` using GPU (CUDA) or CPU with `ffmpeg`.
- `video_subsampler.py`: Subsample a video to a lower FPS using OpenCV.
- `video_fps_change.py`: Change the FPS of a video using OpenCV.
- `gemini_custom_inference.py`: Run inference on videos using Gemini 2.5 Pro API (Google Generative AI).

## Requirements

- Python 3.8+
- `opencv-python` (for FPS scripts)
- `yt-dlp` (for YouTube downloads)
- `ffmpeg` (system dependency)
- `google-generativeai` (for Gemini inference)
- `tqdm` (for progress bars)

Install Python dependencies:
```bash
pip install opencv-python tqdm google-generativeai
```
Install `yt-dlp`:
```bash
pip install yt-dlp
```
Make sure `ffmpeg` is installed and available in your PATH.

## Usage

### Download a YouTube video
```bash
python youtube_downloader.py <video_url> [output_dir]
```

### Download a segment from a YouTube video
```python
from youtube_downloader import download_video_segment
download_video_segment(url, start_time, duration, output_path, fps=25)
```

### Compress all videos in a folder
Place videos in `obfuscated/` and run:
```bash
python video_compressor.py
```

### Subsample video FPS
```bash
python video_subsampler.py
# Or interactively when prompted
```

### Change video FPS
```bash
python video_fps_change.py
# Or interactively when prompted
```

### Gemini 2.5 Pro Inference
Set your API key in the environment: `export API_KEY=...`
```bash
python gemini_custom_inference.py <video_path> <question>
```

---
See each script for more options and details.