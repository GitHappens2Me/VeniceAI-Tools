import cv2
import os
import numpy as np
import re

# Configuration

name = "heaven"
folder = "results\step_animations\\" + f"{name}"
output_video = f"results\\step_animations\\videos\\{name}.mp4"
frame_rate = 10  # FPS
transition_frames = 5  # Number of frames for transition

def extract_number(filename):
    match = re.search(r'_(\d+)\.png$', filename)
    return int(match.group(1)) if match else 0


# Get list of images and sort by the numeric value in the filename
images = sorted([img for img in os.listdir(folder) if img.endswith(('.png', '.jpg', '.jpeg'))], key=extract_number)

print("Processing the following images in order:")
for img in images:
    print(img)

# Load images
frames = []
for img in images:
    img_path = os.path.join(folder, img)
    frame = cv2.imread(img_path)
    frame = cv2.resize(frame, (800, 600))  # Resize to a fixed resolution
    frames.append(frame)

# Create video writer
height, width, _ = frames[0].shape
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_video, fourcc, frame_rate, (width, height))

# Generate smooth transitions
for i in range(len(frames) - 1):
    video.write(frames[i])  # Write original frame
    for t in range(transition_frames):
        alpha = t / transition_frames
        blended = cv2.addWeighted(frames[i], 1 - alpha, frames[i + 1], alpha, 0)
        video.write(blended)  # Write interpolated frame

# Write last frame
video.write(frames[-1])
video.release()

print("Video saved as", output_video)