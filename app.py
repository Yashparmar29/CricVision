from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import cv2
import os
from src.preprocess import extract_landmarks
from src.classify import classify_shot

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', logged_in=True, username=session['username'])
    return render_template('index.html', logged_in=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Dummy authentication
        if username == 'admin' and password == 'password':
            session['username'] = username
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Dummy signup (no storage)
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return jsonify({'error': 'Please log in to upload'})
    file = request.files.get('video')
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        # Process video
        cap = cv2.VideoCapture(filepath)
        landmarks_seq = []
        frame_count = 0
        while cap.isOpened() and frame_count < 100:  # Limit frames for demo
            ret, frame = cap.read()
            if not ret:
                break
            lm = extract_landmarks(frame)
            if lm is not None:
                landmarks_seq.append(lm)
            frame_count += 1
        cap.release()
        os.remove(filepath)  # Clean up
        shot = classify_shot(landmarks_seq)
        return jsonify({'shot': shot, 'frames_processed': len(landmarks_seq)})
    return jsonify({'error': 'No file uploaded'})

if __name__ == '__main__':
    app.run(debug=True)
