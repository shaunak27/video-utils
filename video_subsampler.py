import cv2

def subsample_video_fps(input_video_path, output_video_path, output_fps):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {input_video_path}")
        return

    input_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Compute frame indices to keep
    step = input_fps / output_fps
    frame_indices = [int(i * step) for i in range(int(total_frames / step)) if int(i * step) < total_frames]

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, output_fps, (width, height))

    # Write selected frames
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print(f"Subsampled video saved to {output_video_path} at {output_fps} fps (original fps: {input_fps})")


if __name__ == "__main__":
    input_video = input("Enter input video file path: ")
    output_video = input("Enter output video file path: ")
    fps = float(input("Enter desired output fps (e.g., 1): "))
    subsample_video_fps(input_video, output_video, fps)
