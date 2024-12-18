import cv2
import mediapipe as mp
import numpy as np
import os
from app.config import DRAW_COLOR, MERGED_VIDEO_PATH, OUTPUT_VIDEO_PATH

# Build Keypoints using MP Holistic
mp_holistic = mp.solutions.holistic  # Holistic model
mp_drawing = mp.solutions.drawing_utils  # Drawing utilities

# Define the ignored pose landmarks
IGNORED_POSE_LANDMARKS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 20, 21, 22]

# Create a custom list of connections excluding the ignored landmarks
custom_pose_connections = [
    connection for connection in mp_holistic.POSE_CONNECTIONS
    if connection[0] not in IGNORED_POSE_LANDMARKS and connection[1] not in IGNORED_POSE_LANDMARKS
]

def mediapipe_detection(image, model):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR 2 RGB
    image_rgb.flags.writeable = False  # Image is no longer writable
    results = model.process(image_rgb)  # Make prediction
    image.flags.writeable = True  # Image is now writable
    return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR), results  # Return processed image and results

def draw_styled_landmarks(image, results):
    # Create a blank image with the same dimensions as the original
    mask = np.zeros_like(image)

    # Draw landmarks for face, pose, and hands
    landmarks_to_draw = [
        (results.face_landmarks, mp_holistic.FACEMESH_CONTOURS),
        (results.pose_landmarks, custom_pose_connections),
        (results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS),
        (results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    ]

    for landmarks, connections in landmarks_to_draw:
        if landmarks:
            mp_drawing.draw_landmarks(
                mask,
                landmarks,
                connections,
                None,
                mp_drawing.DrawingSpec(color=DRAW_COLOR, thickness=2, circle_radius=2)
            )

    # Connect wrists
    connect_wrists(mask, results)

    # Show only the landmarks on a black background
    return mask  # Return the mask instead of the original image

def connect_wrists(image, results):
    # Connect pose left wrist to left hand wrist
    if results.pose_landmarks and results.left_hand_landmarks:
        draw_wrist_connection(image, results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_WRIST],
                               results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST])
    # Connect pose right wrist to right hand wrist
    if results.pose_landmarks and results.right_hand_landmarks:
        draw_wrist_connection(image, results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_WRIST],
                               results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST])

def draw_wrist_connection(image, pose_wrist, hand_wrist):
    # Get coordinates for wrists
    pose_wrist_coords = (int(pose_wrist.x * image.shape[1]), int(pose_wrist.y * image.shape[0]))
    hand_wrist_coords = (int(hand_wrist.x * image.shape[1]), int(hand_wrist.y * image.shape[0]))
    # Draw line for wrist connection
    cv2.line(image, pose_wrist_coords, hand_wrist_coords, DRAW_COLOR, thickness=2)

def pose_extraction(video_path=MERGED_VIDEO_PATH, output_path=OUTPUT_VIDEO_PATH):
    # Initialize MediaPipe Holistic
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        cap = cv2.VideoCapture(video_path)
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                image, results = mediapipe_detection(frame, holistic)
                mask = draw_styled_landmarks(image, results)
                out.write(mask)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cap.release()
            out.release()
            cv2.destroyAllWindows()

    return output_path  # Return the path to the processed video
