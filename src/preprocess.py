import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

def extract_landmarks(frame):
    with mp_pose.Pose() as pose:
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
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
