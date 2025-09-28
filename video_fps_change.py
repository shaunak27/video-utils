import os
import json
import cv2

def change_video_fps(input_video_path, output_video_path, output_fps):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {input_video_path}")
        return
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, output_fps, (width, height))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    cap.release()
    out.release()
    print(f"Saved video with {output_fps} fps to {output_video_path}")

if __name__ == "__main__":
    input_video = input("Enter input video file path: ")
    output_video = input("Enter output video file path: ")
    fps = float(input("Enter desired output fps (e.g., 1): "))
    change_video_fps(input_video, output_video, fps)
