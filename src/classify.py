import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os

MODEL_PATH = 'models/shot_classifier.h5'

def build_lstm_model(input_shape=(30, 99)):
    """Build simple LSTM model for shot classification."""
    model = Sequential([
        LSTM(64, input_shape=input_shape, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(4, activation='softmax')  # 4 classes
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def generate_synthetic_data(n_samples=1000):
    """Generate synthetic landmarks sequences for training (simulate shots)."""
    shots = ['cover_drive', 'pull_shot', 'late_cut', 'defensive_push']
    X, y = [], []
    for shot_id, shot_name in enumerate(shots):
        for _ in range(n_samples // 4):
            # Simulate sequence with variations
            base_seq = np.random.rand(30, 99) * 0.1  # Normalized
            if shot_id == 0:  # cover_drive: forward wrist motion
                base_seq[:, 45:48] += np.linspace(0, 0.5, 30)  # right_wrist
            elif shot_id == 1:  # pull: high backlift
                base_seq[:, 30:33] += 0.4  # right_shoulder
            elif shot_id == 2:  # late_cut: late bat angle
                base_seq[:, 60:63] += np.sin(np.linspace(0, np.pi, 30)) * 0.3  # right_elbow
            else:  # defensive: stable
                base_seq += 0.1
            
            X.append(base_seq)
            y.append(shot_id)
    
    X = np.array(X)
    y = tf.keras.utils.to_categorical(y, 4)
    return X, y

def train_model():
    """Train and save model if not exists."""
    if os.path.exists(MODEL_PATH):
        return
    
    os.makedirs('models', exist_ok=True)
    print("Training new LSTM model...")
    
    X, y = generate_synthetic_data()
    model = build_lstm_model()
    
    # Simple training
    model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2, verbose=1)
    
    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

def classify_shot(landmarks_sequence):
    """
    Classify shot using trained LSTM model.
    """
    train_model()  # Ensure model exists
    
    model = load_model(MODEL_PATH)
    
    if not landmarks_sequence or len(landmarks_sequence) == 0:
        return "No shot detected", 0.0
    
    # Prepare input: list -> np array (1,30,99)
    seq = np.array(landmarks_sequence)
    if seq.shape != (30, 99):
        return "Invalid sequence", 0.0
    
    seq = seq.reshape(1, 30, 99)
    
    pred = model.predict(seq, verbose=0)[0]
    shot_id = np.argmax(pred)
    confidence = float(np.max(pred))
    
    shots = ['cover_drive', 'pull_shot', 'late_cut', 'defensive_push']
    return shots[shot_id], confidence

# Placeholder for loading a real model
# def load_model():
#     model = tf.keras.models.load_model('models/lstm_model.h5')
#     return model

# def classify_with_model(model, sequence):
#     # Preprocess sequence
#     # Predict
#     # Return class
