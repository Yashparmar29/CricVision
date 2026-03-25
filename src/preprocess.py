import cv2
import numpy as np
import mediapipe as mp

def extract_landmarks(frame):
    """Extract 33 pose landmarks using MediaPipe."""
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    if results.pose_landmarks:
        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        return np.array(landmarks)
    return None

def calculate_angle(a, b, c):
    # a, b, c are points (x,y,z)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1, 1))
    return np.degrees(angle)

# Function to get specific joint positions
def get_joint_positions(landmarks, joint_indices):
    return np.array([landmarks[i*3:(i+1)*3] for i in joint_indices])

def preprocess_video(video_path, max_frames=30):
    """
    Process video: extract landmarks sequence for LSTM.
    Returns list of landmark vectors (frames x 99).
    """
    cap = cv2.VideoCapture(video_path)
    landmarks_sequence = []
    frame_count = 0
    
    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (640, 480))  # Standardize size
        landmarks = extract_landmarks(frame)
        
        if landmarks is not None:
            landmarks_sequence.append(landmarks)
        
        frame_count += 1
    
    cap.release()
    
    # Pad/truncate to fixed length
    if len(landmarks_sequence) == 0:
        return []
    seq_len = len(landmarks_sequence)
    if seq_len < max_frames:
        pad_len = max_frames - seq_len
        padding = np.zeros((pad_len, 99))
        landmarks_sequence = landmarks_sequence + padding.tolist()
    else:
        landmarks_sequence = landmarks_sequence[:max_frames]
    
    return landmarks_sequence
