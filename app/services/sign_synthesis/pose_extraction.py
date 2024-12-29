import cv2
import mediapipe as mp
import numpy as np
from app.config import DRAW_COLOR, MERGED_VIDEO_PATH, OUTPUT_VIDEO_PATH

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

IGNORED_POSE_LANDMARKS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17, 18, 19, 20, 21, 22]

custom_pose_connections = [
    connection for connection in mp_holistic.POSE_CONNECTIONS
    if connection[0] not in IGNORED_POSE_LANDMARKS and connection[1] not in IGNORED_POSE_LANDMARKS
]

def mediapipe_detection(image, model):
    """
    Converts the image to RGB and processes it using the provided MediaPipe model.

    Args:
        image: The input image in BGR format.
        model: The MediaPipe model to process the image.

    Returns:
        The results from the MediaPipe model.
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model.process(image_rgb)
    return results

def draw_styled_landmarks(image, results):
    """
    Draws styled landmarks on a blank image based on the results from MediaPipe.

    Args:
        image: The original input image.
        results: The results from the MediaPipe model.

    Returns:
        A mask image with the drawn landmarks.
    """
    mask = np.zeros_like(image)
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

    connect_wrists(mask, results)
    return mask

def connect_wrists(image, results):
    """
    Connects the wrists in the pose landmarks to the wrists in the hand landmarks.

    Args:
        image: The image to draw the connections on.
        results: The results from the MediaPipe model.
    """
    if results.pose_landmarks and results.left_hand_landmarks:
        draw_wrist_connection(image, results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_WRIST],
                               results.left_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST])
    if results.pose_landmarks and results.right_hand_landmarks:
        draw_wrist_connection(image, results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_WRIST],
                               results.right_hand_landmarks.landmark[mp_holistic.HandLandmark.WRIST])

def draw_wrist_connection(image, pose_wrist, hand_wrist):
    """
    Draws a line connecting the pose wrist to the hand wrist.

    Args:
        image: The image to draw the connection on.
        pose_wrist: The pose wrist landmark.
        hand_wrist: The hand wrist landmark.
    """
    pose_wrist_coords = (int(pose_wrist.x * image.shape[1]), int(pose_wrist.y * image.shape[0]))
    hand_wrist_coords = (int(hand_wrist.x * image.shape[1]), int(hand_wrist.y * image.shape[0]))
    cv2.line(image, pose_wrist_coords, hand_wrist_coords, DRAW_COLOR, thickness=2)

def pose_extraction(video_path=MERGED_VIDEO_PATH, output_path=OUTPUT_VIDEO_PATH, process_every_nth_frame=2):
    """
    Extracts pose landmarks from a video and saves the output to a new video file.

    Args:
        video_path: The path to the input video file.
        output_path: The path to the output video file.
        process_every_nth_frame: The interval at which frames are processed.

    Returns:
        The path to the output video file.
    """
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        cap = cv2.VideoCapture(video_path)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        try:
            frame_count = 0
            prev_mask = None

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % process_every_nth_frame == 0:
                    results = mediapipe_detection(frame, holistic)
                    if results.pose_landmarks:
                        mask = draw_styled_landmarks(frame, results)
                        prev_mask = mask
                    else:
                       prev_mask = np.zeros_like(frame)

                if prev_mask is not None:
                    out.write(prev_mask)
                else:
                     out.write(np.zeros_like(frame))
                frame_count += 1

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cap.release()
            out.release()
            cv2.destroyAllWindows()

    return output_path
