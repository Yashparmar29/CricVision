from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from src.classify import classify_shot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_key_change_me'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'cricvision.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login required')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/matches')
def matches():
    matches_data = {
        'indian': [
            {
                'id': 'ind1',
                'name': 'IPL 2026 Final',
                'match_type': 'T20',
                'team1': {'flag': 'linear-gradient(135deg, #FF9933, #138808)', 'short': 'CSK', 'name': 'Chennai Super Kings', 'score': '189/4', 'overs': '19.3'},
                'team2': {'flag': 'linear-gradient(135deg, #0066CC, #FFCB05)', 'short': 'MI', 'name': 'Mumbai Indians', 'score': '185/7', 'overs': '20'},
                'status': 'CSK won by 4 wickets',
                'venue': 'MA Chidambaram Stadium, Chennai'
            }
        ],
        'international': [
            {
                'id': 'int1',
                'name': 'India vs Australia - 1st Test',
                'match_type': 'Test',
                'team1': {'flag': 'linear-gradient(135deg, #FF9933, #FFFFFF, #138808)', 'short': 'IND', 'name': 'India', 'score': '571/5d', 'overs': '132.4'},

@app.route('/match/<id>')
def match(id):
    return render_template('match.html')

@app.route('/players')
def players():
    return render_template('players.html')

@app.route('/player/<id>')
def player(id):
    return render_template('player.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')

@app.route('/team/<id>')
def team(id):
    return render_template('team.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        if User.query.filter_by(username=username).first():
            flash('Username taken')
        else:
            user = User(username=username, password_hash=password)
            db.session.add(user)
            db.session.commit()
            flash('Account created! Please login.')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/history')
@login_required
def history():
    return render_template('history.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out')
    return redirect(url_for('index'))

@app.route('/classify', methods=['POST'])
@login_required
def classify():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    # Mock landmarks sequence
    landmarks_sequence = [[0.5, 0.5]] * 25  # Mock 25 frames
    shot = classify_shot(landmarks_sequence)
    return jsonify({'shot': shot, 'confidence': 0.92})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
