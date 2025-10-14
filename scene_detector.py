#!/usr/bin/env python3
"""
Scene Detection for NBA Dataset
Detects scenes in videos and stores frame IDs as metadata JSON files.
Maintains original 60fps frame rate.
"""

import argparse
import json
import os
from pathlib import Path
from scenedetect import open_video, detect, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg
from tqdm import tqdm
import cv2


def detect_scenes(video_path, threshold=20, debug_output_dir=None):
    """
    Detect scenes in a video and return frame IDs.

    Args:
        video_path: Path to the video file
        threshold: Content detection threshold (default: 20)
        debug_output_dir: If provided, save scene clips to this directory

    Returns:
        Dictionary with scene metadata
    """
    # Open video and detect scenes
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    # Detect scenes
    scene_manager.detect_scenes(frame_source=video)
    scene_list = scene_manager.get_scene_list()

    # Get video FPS
    fps = video.frame_rate

    # Convert scenes to frame IDs (keeping original frame numbers at 60fps)
    scenes = []
    for i, scene in enumerate(scene_list):
        start_frame = scene[0].get_frames()
        end_frame = scene[1].get_frames()

        scenes.append({
            "scene_id": i,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "start_time": scene[0].get_seconds(),
            "end_time": scene[1].get_seconds()
        })

    # Prepare metadata
    metadata = {
        "video_path": str(video_path),
        "fps": fps,
        "threshold": threshold,
        "num_scenes": len(scenes),
        "scenes": scenes
    }

    # If debug mode, save scene clips with annotations
    if debug_output_dir and scene_list:
        video_name = Path(video_path).stem
        debug_video_dir = os.path.join(debug_output_dir, video_name)
        os.makedirs(debug_video_dir, exist_ok=True)

        # Split video into scene clips
        split_video_ffmpeg(
            video_path,
            scene_list,
            output_dir=debug_video_dir,
            output_file_template=f"{video_name}_scene_$SCENE_NUMBER.mp4",
            show_progress=False
        )

        # Add text annotations to each clip
        for i, scene in enumerate(scenes):
            clip_path = os.path.join(debug_video_dir, f"{video_name}_scene_{i+1:03d}.mp4")
            if os.path.exists(clip_path):
                annotate_scene_clip(clip_path, scene, fps)

    return metadata


def annotate_scene_clip(clip_path, scene_info, fps):
    """
    Add text annotation overlay to a scene clip.

    Args:
        clip_path: Path to the scene clip
        scene_info: Dictionary with scene metadata
        fps: Frame rate of the video
    """
    # Read the video
    cap = cv2.VideoCapture(clip_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create temporary output path
    temp_path = clip_path.replace('.mp4', '_annotated.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))

    # Prepare annotation text
    annotation = (
        f"Scene {scene_info['scene_id']} | "
        f"Frames: {scene_info['start_frame']}-{scene_info['end_frame']} | "
        f"Time: {scene_info['start_time']:.2f}s-{scene_info['end_time']:.2f}s"
    )

    # Process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Add black background for text
        cv2.rectangle(frame, (10, 10), (width - 10, 60), (0, 0, 0), -1)

        # Add text annotation
        cv2.putText(
            frame,
            annotation,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        out.write(frame)

    cap.release()
    out.release()

    # Replace original with annotated version
    os.replace(temp_path, clip_path)


def process_nba_dataset(data_path, video_dir, output_path, threshold=20, debug_mode=False, debug_limit=5, debug_output_dir=None):
    """
    Process NBA dataset using the same structure as nba_parallel.py.

    Args:
        data_path: Path to JSON file containing video annotations
        video_dir: Directory containing video files
        output_path: Path to save the combined metadata JSON
        threshold: Content detection threshold (default: 20)
        debug_mode: If True, only process first N videos and save clips
        debug_limit: Number of videos to process in debug mode (default: 5)
        debug_output_dir: Directory to save debug clips (default: ./debug_scenes)
    """
    # Load dataset
    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} entries from dataset")

    if debug_mode:
        if debug_output_dir is None:
            debug_output_dir = "./debug_scenes"
        os.makedirs(debug_output_dir, exist_ok=True)
        print(f"Debug mode: Processing first {debug_limit} videos")
        print(f"Debug clips will be saved to: {debug_output_dir}")

    # Filter valid videos and detect scenes
    all_metadata = {}
    valid_count = 0
    processed_count = 0

    for item in tqdm(data, desc="Processing videos"):
        video_filename = item['video']
        video_path = os.path.join(video_dir, video_filename)

        if not os.path.exists(video_path):
            continue

        valid_count += 1

        # In debug mode, stop after processing debug_limit videos
        if debug_mode and processed_count >= debug_limit:
            break

        try:
            metadata = detect_scenes(
                video_path,
                threshold=threshold,
                debug_output_dir=debug_output_dir if debug_mode else None
            )
            all_metadata[video_filename] = metadata
            processed_count += 1

            if debug_mode:
                print(f"\n[{processed_count}/{debug_limit}] Processed {video_filename}: {metadata['num_scenes']} scenes detected")

        except Exception as e:
            print(f"\nError processing {video_filename}: {e}")
            all_metadata[video_filename] = {
                "error": str(e),
                "video_path": video_path
            }

    if debug_mode:
        print(f"\nDebug mode: Processed {processed_count} videos")
        print(f"Scene clips saved to: {debug_output_dir}")
    else:
        print(f"\nProcessed {valid_count} valid videos out of {len(data)} total")

    # Save combined metadata
    output_data = {
        "threshold": threshold,
        "total_videos": processed_count if debug_mode else valid_count,
        "debug_mode": debug_mode,
        "videos": all_metadata
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Scene metadata saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Detect scenes in NBA videos and save frame IDs as metadata")
    parser.add_argument("--data-path", default="shot_test_video.json", help="Path to JSON data file")
    parser.add_argument("--video-dir", default="/coc/testnvme/shalbe3/Grounded-SAM-2/compressed/", help="Directory containing videos")
    parser.add_argument("--global-path", default="/coc/testnvme/shalbe3/F-16-NBA/", help="Global base path")
    parser.add_argument("--output-path", default="scene_metadata.json", help="Output JSON file for scene metadata")
    parser.add_argument("--threshold", type=int, default=20, help="Content detection threshold (default: 20)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode: process only first N videos and save annotated clips")
    parser.add_argument("--debug-limit", type=int, default=5, help="Number of videos to process in debug mode (default: 5)")
    parser.add_argument("--debug-output", default=None, help="Directory to save debug clips (default: ./debug_scenes)")

    args = parser.parse_args()

    # Construct full paths (same logic as nba_parallel.py)
    data_path = os.path.join(args.global_path, args.data_path)
    if args.video_dir.startswith('/'):
        video_dir = args.video_dir
    else:
        video_dir = os.path.join(args.global_path, args.video_dir)
    output_path = os.path.join(args.global_path, args.output_path)

    # Verify paths exist
    if not os.path.exists(data_path):
        print(f"Error: Data file not found: {data_path}")
        return 1

    if not os.path.exists(video_dir):
        print(f"Error: Video directory not found: {video_dir}")
        return 1

    try:
        process_nba_dataset(
            data_path=data_path,
            video_dir=video_dir,
            output_path=output_path,
            threshold=args.threshold,
            debug_mode=args.debug,
            debug_limit=args.debug_limit,
            debug_output_dir=args.debug_output
        )
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
