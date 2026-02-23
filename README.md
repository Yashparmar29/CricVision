CricVision AI: Real-Time Cricket Shot Classifier 🏏🤖
CricVision AI is a Computer Vision project that uses Deep Learning to recognize and classify cricket shots (e.g., Cover Drive, Pull Shot, Late Cut). By tracking the batsman's "skeleton" in 3D space, the system identifies the shot based on biomechanical movement rather than just pixels.

🚀 Overview
Traditional sports analytics requires manual tagging. CricVision AI automates this by:

Extracting skeletal landmarks using MediaPipe.

Analyzing the temporal sequence of movement (how joints move over time).

Classifying the shot using a Neural Network.

🛠️ Tech Stack
Language: Python 3.9+

Computer Vision: OpenCV, MediaPipe

Deep Learning: TensorFlow / Keras

Data Handling: NumPy, Pandas

Deployment (Planned): Streamlit / Flask

📂 Project Structure
Plaintext
├── data/               # Video samples and extracted CSV landmarks
├── models/             # Saved .h5 model files
├── src/
│   ├── collect_data.py # Extracting landmarks from video frames
│   ├── train.py        # LSTM/CNN model training logic
│   └── main.py         # Real-time inference and overlay script
├── requirements.txt    # Project dependencies
└── README.md
⚙️ How It Works
The system follows a 3-step pipeline:

1. Pose Extraction
For every frame, the system tracks 33 key points. For cricket, we focus on:

Shoulders & Hips: To detect torso rotation.

Elbows & Wrists: To track bat swing trajectory.

Knees & Ankles: To identify footwork (front foot vs. back foot).

2. Temporal Processing
Since a "Shot" is a movement, not a still image, we group 30 consecutive frames into a single sequence. This allows the model to see the "flow" of the shot.

3. Classification
The processed sequence is fed into a Long Short-Term Memory (LSTM) network, which is ideal for time-series data like video
