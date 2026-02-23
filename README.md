# 🏏 CricVision AI
### **Real-Time Cricket Shot Classification using Biomechanical Pose Estimation**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-00C7B7?style=for-the-badge&logo=google&logoColor=white)

---

## 🌟 Project Highlights
* **Skeletal Tracking:** Leverages **MediaPipe Pose** to track 33 key body landmarks in 3D space, ensuring accuracy regardless of clothing or background noise.
* **Temporal Intelligence:** Unlike static image classifiers, this uses an **LSTM (Long Short-Term Memory)** architecture to analyze the *sequence* of a shot over 30-60 frames.
* **Biomechanical Analysis:** Calculates real-time joint angles to differentiate between similar movements (e.g., distinguishing a Defensive Push from a Cover Drive).
* **Performance:** Optimized for real-time inference on standard CPUs using coordinate-based feature extraction.

---

## 🧠 The Logic: How It Works
The system identifies shots by calculating the **Cosine Similarity** and **Joint Angles** between specific landmarks. For a **Cover Drive**, the system monitors the angle $\theta$ of the lead knee and the vertical trajectory of the wrists.

The angle between three joints (e.g., Hip, Knee, Ankle) is calculated using the Law of Cosines:

$$\theta = \arccos \left( \frac{a^2 + b^2 - c^2}{2ab} \right)$$

Where:
* $a, b$ are the lengths of the segments connecting the joints.
* $c$ is the distance between the two outer joints.

When the system detects a specific threshold of $\theta$ combined with a forward movement vector, the "Shot" is triggered.

---

## 🛠️ System Architecture

### **1. Frame Processing**
Raw video is ingested at 30 FPS using `OpenCV`. Each frame is converted to RGB and passed to the MediaPipe pipeline.

### **2. Feature Extraction**
We extract $X, Y, Z$ coordinates for the following critical landmarks:
* **Shoulders & Hips:** To measure torso tilt.
* **Elbows & Wrists:** To map the bat swing arc.
* **Knees & Ankles:** To determine front-foot or back-foot dominance.

### **3. Deep Learning Pipeline**
The processed coordinates are fed into an **LSTM Network**:
`Input (Sequence_Length, Landmarks) → LSTM (64 units) → Dense (32) → Softmax (Classification)`

---

## 📂 Project Structure
```text
├── data/               # Raw video clips and extracted CSV landmarks
├── models/             # Pre-trained .h5 or TFLite models
├── src/
│   ├── preprocess.py   # Landmark extraction script
│   ├── train.py        # LSTM Model training logic
│   └── main.py         # Real-time inference & OpenCV overlay
├── requirements.txt    # Project dependencies
└── README.md
