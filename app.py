from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import os
from src.preprocess import extract_landmarks
from src.classify import classify_shot

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yash@localhost/cricvision_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_user():
    return dict(logged_in='username' in session, username=session.get('username'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.pop('username', None) # Clear invalid session
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)

@app.route('/match/<match_id>')
def match_details(match_id):
    return render_template('match.html', match_id=match_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email) | (User.mobile == mobile)).first()
        if existing_user:
            if existing_user.username == username:
                return render_template('signup.html', error='Username already exists')
            elif existing_user.email == email:
                return render_template('signup.html', error='Email already exists')
            else:
                return render_template('signup.html', error='Mobile number already exists')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, mobile=mobile, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

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
