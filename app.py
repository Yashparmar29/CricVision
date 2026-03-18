from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import os
import requests
import uuid
from datetime import datetime
from src.preprocess import extract_landmarks
from src.classify import classify_shot

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads'
# Use SQLite for testing - change to MySQL for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cricvision.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration (configure these for your SMTP server)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Change this
app.config['MAIL_PASSWORD'] = 'your_app_password'  # Change this - use App Password for Gmail
app.config['MAIL_DEFAULT_SENDER'] = 'CricVision AI <your_email@gmail.com>'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Match data structure
MATCH_DATA = {
    "indian": [
        {"id": "ipl-2024-rcb-vs-mi", "name": "IPL 2024", "team1": {"name": "RCB", "short": "RCB", "score": "185/6", "overs": "19.2", "flag": "#d32f2f"}, "team2": {"name": "Mumbai Indians", "short": "MI", "score": "188/5", "overs": "19.1", "flag": "#004ba0"}, "status": "MI won by 5 wickets", "venue": "M Chinnaswamy Stadium, Bengaluru", "match_type": "T20"},
        {"id": "ipl-2024-csk-vs-dc", "name": "IPL 2024", "team1": {"name": "Chennai Super Kings", "short": "CSK", "score": "167/8", "overs": "20", "flag": "#fdd835"}, "team2": {"name": "Delhi Capitals", "short": "DC", "score": "140/10", "overs": "17.4", "flag": "#004ba0"}, "status": "CSK won by 27 runs", "venue": "MA Chidambaram Stadium, Chennai", "match_type": "T20"},
        {"id": "ranji-2024-mumbai-vs-bengal", "name": "Ranji Trophy 2024", "team1": {"name": "Mumbai", "short": "MUM", "score": "312/3", "overs": "85", "flag": "#004ba0"}, "team2": {"name": "Bengal", "short": "BEN", "score": "275/10", "overs": "78.2", "flag": "#ff6f00"}, "status": "Day 2 - Mumbai lead by 37 runs", "venue": "Wankhede Stadium, Mumbai", "match_type": "Test"},
        {"id": "ipl-2024-srh-vs-kkr", "name": "IPL 2024", "team1": {"name": "Sunrisers Hyderabad", "short": "SRH", "score": "201/7", "overs": "20", "flag": "#ff6f00"}, "team2": {"name": "Kolkata Knight Riders", "short": "KKR", "score": "206/4", "overs": "18.5", "flag": "#4a148c"}, "status": "KKR won by 6 wickets", "venue": "Rajiv Gandhi International Stadium, Hyderabad", "match_type": "T20"}
    ],
    "international": [
        {"id": "wtc-2023-24-ind-vs-aus", "name": "WTC Final 2023-24", "team1": {"name": "India", "short": "IND", "score": "314/4", "overs": "82.4", "flag": "#138808"}, "team2": {"name": "Australia", "short": "AUS", "score": "276/10", "overs": "89.1", "flag": "#00008B"}, "status": "Day 3 - India lead by 38 runs", "venue": "The Oval, London", "match_type": "Test"},
        {"id": "t20-wc-2024-ind-vs-eng", "name": "T20 World Cup 2024", "team1": {"name": "India", "short": "IND", "score": "171/7", "overs": "20", "flag": "#138808"}, "team2": {"name": "England", "short": "ENG", "score": "172/3", "overs": "17.2", "flag": "#012169"}, "status": "England won by 7 wickets", "venue": "Providence Stadium, Guyana", "match_type": "T20"},
        {"id": "odi-wc-2023-ind-vs-nz", "name": "Cricket World Cup 2023", "team1": {"name": "India", "short": "IND", "score": "397/4", "overs": "50", "flag": "#138808"}, "team2": {"name": "New Zealand", "short": "NZ", "score": "401/5", "overs": "48.5", "flag": "#000000"}, "status": "New Zealand won by 5 wickets", "venue": "Dharamsala Stadium, Dharamsala", "match_type": "ODI"},
        {"id": "ashes-2023-aus-vs-eng", "name": "Ashes 2023", "team1": {"name": "Australia", "short": "AUS", "score": "386/8", "overs": "93", "flag": "#00008B"}, "team2": {"name": "England", "short": "ENG", "score": "320/10", "overs": "75.1", "flag": "#012169"}, "status": "Day 3 - Australia lead by 66 runs", "venue": "Old Trafford, Manchester", "match_type": "Test"}
    ]
}

PLAYER_DATA = [
    {"id": "virat-kohli", "name": "Virat Kohli", "team": "India", "role": "Batsman", "age": 35, "image": "🟢"},
    {"id": "rohit-sharma", "name": "Rohit Sharma", "team": "India", "role": "Batsman", "age": 37, "image": "🟢"},
    {"id": "jasprit-bumrah", "name": "Jasprit Bumrah", "team": "India", "role": "Bowler", "age": 30, "image": "🟢"},
    {"id": "ms-dhoni", "name": "MS Dhoni", "team": "India", "role": "Wicket Keeper", "age": 43, "image": "🟢"},
    {"id": "hardik-pandya", "name": "Hardik Pandya", "team": "India", "role": "All-Rounder", "age": 30, "image": "🟢"},
    {"id": "ravindra-jadeja", "name": "Ravindra Jadeja", "team": "India", "role": "All-Rounder", "age": 35, "image": "🟢"},
    {"id": "suryakumar-yadav", "name": "Suryakumar Yadav", "team": "India", "role": "Batsman", "age": 33, "image": "🟢"},
    {"id": "shubman-gill", "name": "Shubman Gill", "team": "India", "role": "Batsman", "age": 24, "image": "🟢"},
    {"id": "pat-cummins", "name": "Pat Cummins", "team": "Australia", "role": "Bowler", "age": 31, "image": "🟡"},
    {"id": "steve-smith", "name": "Steve Smith", "team": "Australia", "role": "Batsman", "age": 34, "image": "🟡"},
    {"id": "david-warner", "name": "David Warner", "team": "Australia", "role": "Batsman", "age": 37, "image": "🟡"},
    {"id": "glenn-maxwell", "name": "Glenn Maxwell", "team": "Australia", "role": "All-Rounder", "age": 35, "image": "🟡"},
    {"id": "jos-buttler", "name": "Jos Buttler", "team": "England", "role": "Wicket Keeper", "age": 33, "image": "🔵"},
    {"id": "ben-stokes", "name": "Ben Stokes", "team": "England", "role": "All-Rounder", "age": 32, "image": "🔵"},
    {"id": "joe-root", "name": "Joe Root", "team": "England", "role": "Batsman", "age": 33, "image": "🔵"},
    {"id": "kane-williamson", "name": "Kane Williamson", "team": "New Zealand", "role": "Batsman", "age": 33, "image": "⚫"},
    {"id": "trent-boult", "name": "Trent Boult", "team": "New Zealand", "role": "Bowler", "age": 31, "image": "⚫"},
    {"id": "babar-azam", "name": "Babar Azam", "team": "Pakistan", "role": "Batsman", "age": 29, "image": "🟢"},
    {"id": "shaheen-shah", "name": "Shaheen Shah Afridi", "team": "Pakistan", "role": "Bowler", "age": 24, "image": "🟢"},
    {"id": "rahmanullah-gurbaz", "name": "Rahmanullah Gurbaz", "team": "Afghanistan", "role": "Wicket Keeper", "age": 22, "image": "🔴"}
]

TEAM_DATA = [
    {"id": "india", "name": "India", "short": "IND", "flag": "#138808", "rank": 1},
    {"id": "australia", "name": "Australia", "short": "AUS", "flag": "#00008B", "rank": 2},
    {"id": "england", "name": "England", "short": "ENG", "flag": "#012169", "rank": 3},
    {"id": "new-zealand", "name": "New Zealand", "short": "NZ", "flag": "#000000", "rank": 4},
    {"id": "pakistan", "name": "Pakistan", "short": "PAK", "flag": "#006600", "rank": 5},
    {"id": "south-africa", "name": "South Africa", "short": "SA", "flag": "#006400", "rank": 6},
    {"id": "sri-lanka", "name": "Sri Lanka", "short": "SL", "flag": "#000080", "rank": 7},
    {"id": "afghanistan", "name": "Afghanistan", "short": "AFG", "flag": "#ED1C24", "rank": 8},
    {"id": "bangladesh", "name": "Bangladesh", "short": "BAN", "flag": "#006A4E", "rank": 9},
    {"id": "west-indies", "name": "West Indies", "short": "WI", "flag": "#FF0000", "rank": 10},
    {"id": "rcb", "name": "Royal Challengers Bangalore", "short": "RCB", "flag": "#d32f2f", "rank": 0},
    {"id": "mi", "name": "Mumbai Indians", "short": "MI", "flag": "#004ba0", "rank": 0},
    {"id": "csk", "name": "Chennai Super Kings", "short": "CSK", "flag": "#fdd835", "rank": 0},
    {"id": "kkr", "name": "Kolkata Knight Riders", "short": "KKR", "flag": "#4a148c", "rank": 0},
    {"id": "srh", "name": "Sunrisers Hyderabad", "short": "SRH", "flag": "#ff6f00", "rank": 0},
    {"id": "dc", "name": "Delhi Capitals", "short": "DC", "flag": "#004ba0", "rank": 0}
]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(64), unique=True, nullable=True)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shot_type = db.Column(db.String(50), nullable=False)
    frames_processed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('analyses', lazy=True))

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favorite_type = db.Column(db.String(20), nullable=False)
    favorite_id = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Email sending function
def send_verification_email(user):
    """Send verification email to user"""
    token = str(uuid.uuid4())
    user.verification_token = token
    db.session.commit()
    
    # Create email message
    msg = MIMEMultipart()
    msg['From'] = app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = user.email
    msg['Subject'] = 'Verify your CricVision AI Account'
    
    # Email body
    verification_url = url_for('verify_email', token=token, _external=True)
    body = f"""Hello {user.username},

Welcome to CricVision AI!

Please verify your email address by clicking the link below:
{verification_url}

If you didn't create an account, please ignore this email.

Best regards,
CricVision AI Team
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # For testing, we'll simulate sending (print to console)
        # In production, uncomment the SMTP code below
        print(f"\n=== EMAIL VERIFICATION ===")
        print(f"To: {user.email}")
        print(f"Verification URL: {verification_url}")
        print(f"===========================\n")
        
        # Uncomment below for actual email sending:
        # server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        # server.starttls()
        # server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        # server.send_message(msg)
        # server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

with app.app_context():
    db.create_all()
    if Player.query.count() == 0:
        for p in PLAYER_DATA:
            player = Player(player_id=p['id'], name=p['name'], team=p['team'], role=p['role'], age=p['age'], image=p['image'])
            db.session.add(player)
        db.session.commit()

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
    user = User.query.filter_by(username=session['username']).first()
    if user and not user.is_verified:
        return render_template('dashboard.html', verification_pending=True)
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.pop('username', None)
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)

@app.route('/matches')
def matches():
    return render_template('matches.html', matches=MATCH_DATA)

@app.route('/match/<match_id>')
def match_details(match_id):
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

@app.route('/players')
def players():
    search_query = request.args.get('search', '')
    team_filter = request.args.get('team', '')
    players_list = Player.query
    if search_query:
        players_list = players_list.filter(Player.name.ilike(f'%{search_query}%'))
    if team_filter:
        players_list = players_list.filter(Player.team.ilike(f'%{team_filter}%'))
    players_list = players_list.all()
    teams = db.session.query(Player.team).distinct().all()
    teams = [t[0] for t in teams]
    return render_template('players.html', players=players_list, teams=teams, search_query=search_query, team_filter=team_filter)

@app.route('/player/<player_id>')
def player_details(player_id):
    player = Player.query.filter_by(player_id=player_id).first()
    if not player:
        player = Player.query.filter_by(name=player_id.replace('-', ' ').title()).first()
    if not player:
        return render_template('players.html', error="Player not found", players=Player.query.all(), teams=[], search_query='', team_filter='')
    is_favorite = False
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            fav = Favorite.query.filter_by(user_id=user.id, favorite_type='player', favorite_id=player.player_id).first()
            is_favorite = fav is not None
    return render_template('player.html', player=player, is_favorite=is_favorite)

@app.route('/teams')
def teams():
    return render_template('teams.html', teams=TEAM_DATA)

@app.route('/team/<team_id>')
def team_details(team_id):
    team = None
    for t in TEAM_DATA:
        if t['id'] == team_id:
            team = t
            break
    if not team:
        return render_template('teams.html', error="Team not found", teams=TEAM_DATA)
    team_players = Player.query.filter_by(team=team['name']).all()
    return render_template('team.html', team=team, players=team_players)

@app.route('/leaderboard')
def leaderboard():
    top_users = User.query.order_by(User.analyses_count.desc()).limit(20).all()
    return render_template('leaderboard.html', users=top_users)

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.pop('username', None)
        return redirect(url_for('login'))
    analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).all()
    return render_template('history.html', analyses=analyses, user=user)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.pop('username', None)
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_email = request.form.get('email')
        new_mobile = request.form.get('mobile')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if not check_password_hash(user.password_hash, current_password):
            return render_template('settings.html', user=user, error='Current password is incorrect')
        if new_email and new_email != user.email:
            existing = User.query.filter(User.email == new_email, User.id != user.id).first()
            if existing:
                return render_template('settings.html', user=user, error='Email already in use')
            user.email = new_email
            user.is_verified = False  # Re-verify if email changes
            send_verification_email(user)
        if new_mobile and new_mobile != user.mobile:
            existing = User.query.filter(User.mobile == new_mobile, User.id != user.id).first()
            if existing:
                return render_template('settings.html', user=user, error='Mobile number already in use')
            user.mobile = new_mobile
        if new_password:
            user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return render_template('settings.html', user=user, success='Settings updated successfully!')
    return render_template('settings.html', user=user)

# Email verification route
@app.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        return render_template('login.html', success='Email verified successfully! Please login.')
    return render_template('login.html', error='Invalid or expired verification link.')

# Resend verification email
@app.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.is_verified:
                return render_template('resend_verification.html', error='Email already verified. Please login.')
            if send_verification_email(user):
                return render_template('resend_verification.html', success='Verification email sent! Please check your inbox (also check spam folder).')
            else:
                return render_template('resend_verification.html', error='Failed to send email. Please try again.')
        else:
            return render_template('resend_verification.html', error='No account found with this email address.')
    return render_template('resend_verification.html')

@app.route('/api/matches')
def get_all_matches():
    return jsonify(MATCH_DATA)

@app.route('/api/matches/<category>')
def get_matches_by_category(category):
    if category in MATCH_DATA:
        return jsonify(MATCH_DATA[category])
    return jsonify({"error": "Category not found"}), 404

@app.route('/api/match/<match_id>')
def get_match_details(match_id):
    for category in MATCH_DATA:
        for match in MATCH_DATA[category]:
            if match['id'] == match_id:
                return jsonify(match)
    return jsonify({"error": "Match not found"}), 404

@app.route('/api/players')
def get_players():
    search = request.args.get('search', '')
    team = request.args.get('team', '')
    players_query = Player.query
    if search:
        players_query = players_query.filter(Player.name.ilike(f'%{search}%'))
    if team:
        players_query = players_query.filter(Player.team.ilike(f'%{team}%'))
    players = players_query.all()
    return jsonify([{'id': p.player_id, 'name': p.name, 'team': p.team, 'role': p.role, 'age': p.age, 'image': p.image} for p in players])

@app.route('/api/player/<player_id>')
def get_player(player_id):
    player = Player.query.filter_by(player_id=player_id).first()
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({'id': player.player_id, 'name': player.name, 'team': player.team, 'role': player.role, 'age': player.age, 'image': player.image})

@app.route('/api/teams')
def get_teams():
    return jsonify(TEAM_DATA)

@app.route('/api/leaderboard')
def get_leaderboard():
    top_users = User.query.order_by(User.analyses_count.desc()).limit(20).all()
    return jsonify([{'rank': i+1, 'username': u.username, 'analyses_count': u.analyses_count, 'created_at': u.created_at.isoformat() if u.created_at else None} for i, u in enumerate(top_users)])

@app.route('/api/history')
def get_history():
    if 'username' not in session:
        return jsonify({'error': 'Please log in'}), 401
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).all()
    return jsonify([{'id': a.id, 'shot_type': a.shot_type, 'frames_processed': a.frames_processed, 'created_at': a.created_at.isoformat() if a.created_at else None} for a in analyses])

@app.route('/api/favorites', methods=['GET', 'POST', 'DELETE'])
def manage_favorites():
    if 'username' not in session:
        return jsonify({'error': 'Please log in'}), 401
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if request.method == 'GET':
        favorites = Favorite.query.filter_by(user_id=user.id).all()
        return jsonify([{'id': f.id, 'type': f.favorite_type, 'favorite_id': f.favorite_id} for f in favorites])
    elif request.method == 'POST':
        data = request.get_json()
        favorite_type = data.get('type')
        favorite_id = data.get('favorite_id')
        if not favorite_type or not favorite_id:
            return jsonify({'error': 'Missing required fields'}), 400
        existing = Favorite.query.filter_by(user_id=user.id, favorite_type=favorite_type, favorite_id=favorite_id).first()
        if existing:
            return jsonify({'message': 'Already in favorites'})
        new_fav = Favorite(user_id=user.id, favorite_type=favorite_type, favorite_id=favorite_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({'message': 'Added to favorites'})
    elif request.method == 'DELETE':
        data = request.get_json()
        favorite_id = data.get('favorite_id')
        fav = Favorite.query.filter_by(id=favorite_id, user_id=user.id).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return jsonify({'message': 'Removed from favorites'})
        return jsonify({'error': 'Favorite not found'}), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                return render_template('login.html', error='Please verify your email first. Check your inbox for the verification link.')
            session['username'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        
        # Validate that all required fields are present
        if not username or not email or not mobile or not password:
            return render_template('signup.html', error='All fields are required. Please fill in all fields.')
        
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
        
        # Send verification email
        send_verification_email(new_user)
        
        return render_template('login.html', success='Account created! Please check your email to verify your account before logging in.')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return jsonify({'error': 'Please log in to upload'})
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        session.pop('username', None)
        return jsonify({'error': 'Please log in to upload'})
    
    # Check if email is verified
    if not user.is_verified:
        return jsonify({'error': 'Please verify your email before uploading videos'})
    
    file = request.files.get('video')
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        cap = cv2.VideoCapture(filepath)
        landmarks_seq = []
        frame_count = 0
        while cap.isOpened() and frame_count < 100:
            ret, frame = cap.read()
            if not ret:
                break
            lm = extract_landmarks(frame)
            if lm is not None:
                landmarks_seq.append(lm)
            frame_count += 1
        cap.release()
        os.remove(filepath)
        
        shot = classify_shot(landmarks_seq)
        
        analysis = Analysis(user_id=user.id, shot_type=shot, frames_processed=len(landmarks_seq))
        db.session.add(analysis)
        user.analyses_count += 1
        db.session.commit()
        
        return jsonify({'shot': shot, 'frames_processed': len(landmarks_seq)})
    return jsonify({'error': 'No file uploaded'})

if __name__ == '__main__':
    app.run(debug=True)
