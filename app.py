from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import os
import requests
from src.preprocess import extract_landmarks
from src.classify import classify_shot

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yash@localhost/cricvision_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Match data structure
MATCH_DATA = {
    "indian": [
        {
            "id": "ipl-2024-rcb-vs-mi",
            "name": "IPL 2024",
            "team1": {"name": "RCB", "short": "RCB", "score": "185/6", "overs": "19.2", "flag": "#d32f2f"},
            "team2": {"name": "Mumbai Indians", "short": "MI", "score": "188/5", "overs": "19.1", "flag": "#004ba0"},
            "status": "MI won by 5 wickets",
            "venue": "M Chinnaswamy Stadium, Bengaluru",
            "match_type": "T20"
        },
        {
            "id": "ipl-2024-csk-vs-dc",
            "name": "IPL 2024",
            "team1": {"name": "Chennai Super Kings", "short": "CSK", "score": "167/8", "overs": "20", "flag": "#fdd835"},
            "team2": {"name": "Delhi Capitals", "short": "DC", "score": "140/10", "overs": "17.4", "flag": "#004ba0"},
            "status": "CSK won by 27 runs",
            "venue": "MA Chidambaram Stadium, Chennai",
            "match_type": "T20"
        },
        {
            "id": "ranji-2024-mumbai-vs-bengal",
            "name": "Ranji Trophy 2024",
            "team1": {"name": "Mumbai", "short": "MUM", "score": "312/3", "overs": "85", "flag": "#004ba0"},
            "team2": {"name": "Bengal", "short": "BEN", "score": "275/10", "overs": "78.2", "flag": "#ff6f00"},
            "status": "Day 2 - Mumbai lead by 37 runs",
            "venue": "Wankhede Stadium, Mumbai",
            "match_type": "Test"
        },
        {
            "id": "ipl-2024-srh-vs-kkr",
            "name": "IPL 2024",
            "team1": {"name": "Sunrisers Hyderabad", "short": "SRH", "score": "201/7", "overs": "20", "flag": "#ff6f00"},
            "team2": {"name": "Kolkata Knight Riders", "short": "KKR", "score": "206/4", "overs": "18.5", "flag": "#4a148c"},
            "status": "KKR won by 6 wickets",
            "venue": "Rajiv Gandhi International Stadium, Hyderabad",
            "match_type": "T20"
        }
    ],
    "international": [
        {
            "id": "wtc-2023-24-ind-vs-aus",
            "name": "WTC Final 2023-24",
            "team1": {"name": "India", "short": "IND", "score": "314/4", "overs": "82.4", "flag": "#138808"},
            "team2": {"name": "Australia", "short": "AUS", "score": "276/10", "overs": "89.1", "flag": "#00008B"},
            "status": "Day 3 - India lead by 38 runs",
            "venue": "The Oval, London",
            "match_type": "Test"
        },
        {
            "id": "t20-wc-2024-ind-vs-eng",
            "name": "T20 World Cup 2024",
            "team1": {"name": "India", "short": "IND", "score": "171/7", "overs": "20", "flag": "#138808"},
            "team2": {"name": "England", "short": "ENG", "score": "172/3", "overs": "17.2", "flag": "#012169"},
            "status": "England won by 7 wickets",
            "venue": "Providence Stadium, Guyana",
            "match_type": "T20"
        },
        {
            "id": "odi-wc-2023-ind-vs-nz",
            "name": "Cricket World Cup 2023",
            "team1": {"name": "India", "short": "IND", "score": "397/4", "overs": "50", "flag": "#138808"},
            "team2": {"name": "New Zealand", "short": "NZ", "score": "401/5", "overs": "48.5", "flag": "#000000"},
            "status": "New Zealand won by 5 wickets",
            "venue": "Dharamsala Stadium, Dharamsala",
            "match_type": "ODI"
        },
        {
            "id": "ashes-2023-aus-vs-eng",
            "name": "Ashes 2023",
            "team1": {"name": "Australia", "short": "AUS", "score": "386/8", "overs": "93", "flag": "#00008B"},
            "team2": {"name": "England", "short": "ENG", "score": "320/10", "overs": "75.1", "flag": "#012169"},
            "status": "Day 3 - Australia lead by 66 runs",
            "venue": "Old Trafford, Manchester",
            "match_type": "Test"
        }
    ]
}

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

@app.route('/matches')
def matches():
    """Page to select and view matches"""
    return render_template('matches.html', matches=MATCH_DATA)

@app.route('/match/<match_id>')
def match_details(match_id):
    """Get specific match details"""
    # Search for the match in all categories
    match = None
    for category in MATCH_DATA:
        for m in MATCH_DATA[category]:
            if m['id'] == match_id:
                match = m
                break
        if match:
            break
    
    if not match:
        return render_template('match.html', match=None, error="Match not found")
    
    return render_template('match.html', match=match)

@app.route('/api/matches')
def get_all_matches():
    """API to get all matches grouped by category"""
    return jsonify(MATCH_DATA)

@app.route('/api/matches/<category>')
def get_matches_by_category(category):
    """API to get matches by category (indian/international)"""
    if category in MATCH_DATA:
        return jsonify(MATCH_DATA[category])
    return jsonify({"error": "Category not found"}), 404

@app.route('/api/match/<match_id>')
def get_match_details(match_id):
    """API to get specific match details"""
    for category in MATCH_DATA:
        for match in MATCH_DATA[category]:
            if match['id'] == match_id:
                return jsonify(match)
    return jsonify({"error": "Match not found"}), 404

@app.route('/api/cricket-players/<team_id>', methods=['GET'])
def get_cricket_players(team_id):
    """
    Fetch cricket players from RapidAPI for a given team ID
    """
    url = f"https://cricket-api-free-data.p.rapidapi.com/cricket-players?teamid={team_id}"
    headers = {
        'x-rapidapi-host': 'cricket-api-free-data.p.rapidapi.com',
        'x-rapidapi-key': '5779d8b25dmshee45fe2a8032447p107533jsn6b83c0c7e97a'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'API request failed with status {response.status_code}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
