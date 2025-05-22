from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import uuid
from init_db import init_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '..')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'oytammifkflipyfx')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'okikiolatoloruntomi1234@gmail.com')

# Debug print email configuration
print("Email Configuration:")
print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
print("MAIL_PASSWORD: [HIDDEN]")

# Initialize extensions
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join('static', 'img'), exist_ok=True)

# Initialize database
if not os.path.exists('users.json'):
    init_db()

# User data management functions
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "settings": {
            "default_points": 400,
            "points_per_10mb": 15,
            "max_file_size_free": 500,
            "file_expiry_days": 10
        }}

def save_users(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4)

def get_user_by_email(email):
    data = load_users()
    for user in data['users']:
        if user['email'] == email:
            return user
    return None

def get_user_by_id(user_id):
    data = load_users()
    try:
        return data['users'][user_id]
    except IndexError:
        return None

def add_user(user_data):
    data = load_users()
    user_data['id'] = len(data['users'])
    data['users'].append(user_data)
    save_users(data)
    return user_data

def update_user(user_id, user_data):
    data = load_users()
    if 0 <= user_id < len(data['users']):
        data['users'][user_id].update(user_data)
        save_users(data)
        return True
    return False

def delete_user(user_id):
    data = load_users()
    if 0 <= user_id < len(data['users']):
        data['users'].pop(user_id)
        save_users(data)
        return True
    return False

# File data management functions
def load_files():
    if not os.path.exists('files.json'):
        with open('files.json', 'w') as f:
            json.dump({'files': [], 'settings': {
                'max_file_size': 524288000,
                'expiry_days': 7,
                'points_per_10mb': 1
            }}, f, indent=4)
    with open('files.json', 'r') as f:
        return json.load(f)

def save_files(data):
    with open('files.json', 'w') as f:
        json.dump(data, f, indent=4)

def get_file_by_id(file_id):
    data = load_files()
    for file in data['files']:
        if file['id'] == file_id:
            return file
    return None

def add_file(file_data):
    data = load_files()
    file_data['id'] = len(data['files']) + 1
    data['files'].append(file_data)
    save_files(data)
    return file_data

def update_file(file_id, file_data):
    data = load_files()
    for i, file in enumerate(data['files']):
        if file['id'] == file_id:
            data['files'][i] = file_data
            save_files(data)
            return file_data
    return None

def delete_file(file_id):
    data = load_files()
    for i, file in enumerate(data['files']):
        if file['id'] == file_id:
            del data['files'][i]
            save_files(data)
            return True
    return False

def get_user_files(user_id):
    data = load_files()
    return [file for file in data['files'] if file['user_id'] == user_id]

def get_shared_files(user_id):
    data = load_files()
    return [file for file in data['files'] if file['shared_by'] == user_id]

# Models
class User(UserMixin):
    def __init__(self, id, username, email, password_hash, points=400, is_premium=False, 
                 is_verified=False, is_admin=False, profile_picture='default.jpg', 
                 email_notifications=True, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.points = points
        self.is_premium = is_premium
        self.is_verified = is_verified
        self.is_admin = is_admin
        self.profile_picture = profile_picture
        self.email_notifications = email_notifications
        self.created_at = created_at or datetime.utcnow()
        self.recent_activity = []

    @staticmethod
    def from_dict(data):
        return User(
            id=data['id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            points=data.get('points', 400),
            is_premium=data.get('is_premium', False),
            is_verified=data.get('is_verified', False),
            is_admin=data.get('is_admin', False),
            profile_picture=data.get('profile_picture', 'default.jpg'),
            email_notifications=data.get('email_notifications', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'points': self.points,
            'is_premium': self.is_premium,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'profile_picture': self.profile_picture,
            'email_notifications': self.email_notifications,
            'created_at': self.created_at.isoformat()
        }

class File:
    def __init__(self, id, filename, unique_filename, file_size, user_id, shared_by=None, expiry_date=None, upload_date=None):
        self.id = str(id)  # Convert ID to string to ensure consistent handling
        self.filename = filename
        self.unique_filename = unique_filename
        self.file_size = file_size
        self.user_id = user_id
        self.shared_by = shared_by
        self.expiry_date = expiry_date or (datetime.utcnow() + timedelta(days=7))
        self.upload_date = upload_date or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        return File(
            id=str(data['id']),  # Ensure ID is converted to string
            filename=data['filename'],
            unique_filename=data['unique_filename'],
            file_size=data['file_size'],
            user_id=data['user_id'],
            shared_by=data.get('shared_by'),
            expiry_date=datetime.fromisoformat(data['expiry_date']) if data.get('expiry_date') else None,
            upload_date=datetime.fromisoformat(data['upload_date']) if data.get('upload_date') else None
        )

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'unique_filename': self.unique_filename,
            'file_size': self.file_size,
            'user_id': self.user_id,
            'shared_by': self.shared_by,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }

@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(int(user_id))
    if user_data:
        return User.from_dict(user_data)
    return None

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/access', methods=['GET', 'POST'])
def access():
    if request.method == 'POST':
        if request.form['password'] == os.getenv('GENERAL_ACCESS_PASSWORD', 'welcome123'):
            session['has_access'] = True
            return redirect(url_for('index'))
        flash('Invalid access password')
    return render_template('access.html')

@app.route('/welcome')
def welcome():
    if 'first_visit' in session:
        session.pop('first_visit', None)
        return render_template('welcome.html')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_data = get_user_by_email(request.form['email'])
        if user_data and check_password_hash(user_data['password_hash'], request.form['password']):
            user = User.from_dict(user_data)
            remember = 'remember' in request.form
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if get_user_by_email(request.form['email']):
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user_data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'password_hash': generate_password_hash(request.form['password']),
            'points': 400,
            'is_premium': False,
            'is_verified': False,
            'is_admin': False,
            'profile_picture': 'default.jpg'
        }
        
        add_user(user_data)
        
        # Send verification email
        token = generate_verification_token(user_data['email'])
        send_verification_email(user_data['email'], token)
        
        flash('Please check your email to verify your account')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_data = get_user_by_id(current_user.id)
    owned_files = [File.from_dict(f) for f in get_user_files(current_user.id)]
    shared_files = [File.from_dict(f) for f in get_shared_files(current_user.id)]
    
    # Debug print to check file IDs
    for file in owned_files:
        print(f"File ID: {file.id}, Filename: {file.filename}, Type: {type(file.id)}")
    
    return render_template('dashboard.html', 
                         user=user_data,
                         owned_files=owned_files,
                         shared_files=shared_files)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('dashboard'))
    
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        settings = load_files()['settings']
        
        if file_size > settings['max_file_size']:
            os.remove(file_path)
            flash('File too large')
            return redirect(url_for('dashboard'))
        
        points_required = (file_size // (10 * 1024 * 1024)) * settings['points_per_10mb']
        user_data = get_user_by_id(current_user.id)
        
        if user_data['points'] < points_required:
            os.remove(file_path)
            flash('Not enough points')
            return redirect(url_for('dashboard'))
        
        user_data['points'] -= points_required
        update_user(current_user.id, user_data)
        
        current_time = datetime.utcnow()
        file_data = {
            'filename': filename,
            'unique_filename': unique_filename,
            'file_size': file_size,
            'user_id': current_user.id,
            'shared_by': current_user.id,
            'expiry_date': (current_time + timedelta(days=settings['expiry_days'])).isoformat(),
            'upload_date': current_time.isoformat()
        }
        
        add_file(file_data)
        flash('File uploaded successfully')
    return redirect(url_for('dashboard'))

@app.route('/download/<int:file_id>')
def download_file(file_id):
    file_data = get_file_by_id(file_id)
    if not file_data:
        flash('File not found')
        return redirect(url_for('index'))
    
    file = File.from_dict(file_data)
    
    # Check if download parameter is present
    if request.args.get('download'):
        return send_from_directory(app.config['UPLOAD_FOLDER'], 
                                 file.unique_filename, 
                                 as_attachment=True, 
                                 download_name=file.filename)
    
    # If no download parameter, show the file view page
    return render_template('file_view.html', file=file)

@app.route('/share/<int:file_id>', methods=['POST'])
@login_required
def share_file(file_id):
    file_data = get_file_by_id(file_id)
    if not file_data:
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    if file_data['user_id'] != current_user.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if request.is_json:
        data = request.get_json()
        email = data.get('email')
        if email:
            # Send email with download link
            msg = Message('File Shared with You',
                         recipients=[email])
            msg.body = f'''Hello,

{current_user.username} has shared a file with you.

You can download the file using this link:
{url_for('download_file', file_id=file_id, _external=True)}

This link will expire on {file_data['expiry_date']}.

Best regards,
File Sharing App Team'''
            try:
                mail.send(msg)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
    
    # For direct sharing, update the shared_by field
    file_data['shared_by'] = current_user.id
    update_file(file_id, file_data)
    return jsonify({'success': True})

@app.route('/delete/<int:file_id>')
@login_required
def delete_file(file_id):
    file_data = get_file_by_id(file_id)
    if not file_data:
        flash('File not found')
        return redirect(url_for('dashboard'))
    
    if file_data['user_id'] != current_user.id:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_data['unique_filename']))
    delete_file(file_id)
    flash('File deleted successfully')
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    user_data = get_user_by_id(current_user.id)
    user = User.from_dict(user_data)
    return render_template('profile.html', user=user)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        user_data = get_user_by_id(current_user.id)
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join('static', 'img', unique_filename))
                user_data['profile_picture'] = unique_filename
        
        if request.form.get('username'):
            user_data['username'] = request.form['username']
        
        if request.form.get('email'):
            user_data['email'] = request.form['email']
        
        if request.form.get('current_password') and request.form.get('new_password'):
            if check_password_hash(user_data['password_hash'], request.form['current_password']):
                user_data['password_hash'] = generate_password_hash(request.form['new_password'])
            else:
                flash('Current password is incorrect')
                return redirect(url_for('settings'))
        
        update_user(current_user.id, user_data)
        flash('Settings updated successfully')
        return redirect(url_for('settings'))
    
    user_data = get_user_by_id(current_user.id)
    return render_template('settings.html', user=user_data)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    users = load_users()
    files = load_files()
    return render_template('admin.html', 
                         users=users['users'],
                         files=[File.from_dict(f) for f in files['files']],
                         settings=files['settings'])

@app.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_user(user_id):
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    user_data = get_user_by_id(user_id)
    if not user_data:
        flash('User not found')
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        user_data.update({
            'username': request.form['username'],
            'email': request.form['email'],
            'points': int(request.form['points']),
            'is_premium': 'is_premium' in request.form,
            'is_verified': 'is_verified' in request.form,
            'is_admin': 'is_admin' in request.form
        })
        update_user(user_id, user_data)
        flash('User updated successfully')
        return redirect(url_for('admin'))
    
    user_files = [File.from_dict(f) for f in get_user_files(user_id)]
    shared_files = [File.from_dict(f) for f in get_shared_files(user_id)]
    
    return render_template('admin_user.html', 
                         user=user_data,
                         user_files=user_files,
                         shared_files=shared_files)

@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = verify_token(token)
        user_data = get_user_by_email(email)
        if user_data:
            user_data['is_verified'] = True
            update_user(user_data['id'], user_data)
            flash('Email verified successfully')
        else:
            flash('Invalid verification link')
    except:
        flash('Invalid or expired verification link')
    return redirect(url_for('login'))

def verify_token(token):
    # Simple token verification - in production, use a more secure method
    try:
        # For now, token is just the email itself
        return token
    except:
        return None

def generate_verification_token(email):
    # Simple token generation - in production, use a more secure method
    return email

def send_verification_email(email, token):
    msg = Message('Verify your email',
                  recipients=[email])
    msg.body = f'Click the following link to verify your email: {url_for("verify_email", token=token, _external=True)}'
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send verification email: {str(e)}")
        # Continue with signup process even if email fails
        pass

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/api/user/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        user = get_user_by_id(user_id)
        if user:
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404

    elif request.method == 'PUT':
        data = request.get_json()
        if update_user(user_id, data):
            return jsonify({'success': True})
        return jsonify({'error': 'User not found'}), 404

    elif request.method == 'DELETE':
        if delete_user(user_id):
            return jsonify({'success': True})
        return jsonify({'error': 'User not found'}), 404

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        files_data = load_files()
        files_data['settings'].update({
            'max_file_size': int(request.form['max_file_size']),
            'expiry_days': int(request.form['expiry_days']),
            'points_per_10mb': int(request.form['points_per_10mb'])
        })
        save_files(files_data)
        flash('Settings updated successfully')
        return redirect(url_for('admin'))
    
    files_data = load_files()
    return render_template('admin_settings.html', settings=files_data['settings'])

if __name__ == '__main__':
    app.run(debug=True, port=5001) 