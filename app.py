prefrom flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from src.classify import classify_shot
from src.preprocess import preprocess_video
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_key_change_me'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
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
    analyses = db.relationship('Analysis', backref='user', lazy=True)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    shot = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

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

# Fix incomplete matches route
@app.route('/matches')
def matches():
    matches_data = {
        'indian': [
            {
                'id': 'ind1',
                'name': 'IPL 2026 Final',
                'match_type': 'T20',
                'date': 'May 2026'
            }
        ],
        'international': [
            {
                'id': 'int1',
                'name': 'India vs Australia Test',
                'match_type': 'Test',
                'date': 'Dec 2025'
            }
        ]
    }
    return render_template('matches.html', matches=matches_data)

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
                'date': 'May 2026'
            }
        ],
        'international': [
            {
                'id': 'int1',
                'name': 'India vs Australia Test',
                'match_type': 'Test',
                'date': 'Dec 2025'
            }
        ]
    }
    return render_template('matches.html', matches=matches_data)

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
@login_required
def leaderboard():
    from sqlalchemy import func
    # Top users by analysis count
    top_users = db.session.query(
        User, 
        func.count(Analysis.id).label('count')
    ).outerjoin(Analysis).group_by(User.id).order_by('count desc').limit(10).all()
    return render_template('leaderboard.html', top_users=top_users)

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
    analyses = Analysis.query.filter_by(user_id=session['user_id']).order_by(Analysis.created_at.desc()).limit(20).all()
    return render_template('history.html', analyses=analyses)

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
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'})
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Real processing
    landmarks_sequence = preprocess_video(filepath)
    shot, confidence = classify_shot(landmarks_sequence)
    
    # Save to DB
    analysis = Analysis(
        user_id=session['user_id'],
        filename=filename,
        shot=shot,
        confidence=confidence
    )
    db.session.add(analysis)
    db.session.commit()
    
    return jsonify({
        'shot': shot,
        'confidence': confidence,
        'filename': filename
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
