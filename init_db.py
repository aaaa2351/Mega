import os
import json
from werkzeug.security import generate_password_hash

def init_db():
    # Create upload directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    
    # Initialize users.json if it doesn't exist
    if not os.path.exists('users.json'):
        default_data = {
            'users': [],
            'settings': {
                'default_points': 400,
                'points_per_10mb': 1,
                'max_file_size_free': 500 * 1024 * 1024,  # 500MB
                'file_expiry_days': 7
            }
        }
        with open('users.json', 'w') as f:
            json.dump(default_data, f, indent=4)
    
    # Load existing users
    with open('users.json', 'r') as f:
        data = json.load(f)
    
    # Check if admin user exists
    admin_exists = any(user['email'] == 'admin@admin.com' for user in data['users'])
    
    if not admin_exists:
        admin_user = {
            'id': 1,
            'username': 'admin',
            'email': 'admin@admin.com',
            'password_hash': generate_password_hash('admin123'),
            'points': 1000,
            'is_premium': True,
            'is_verified': True,
            'is_admin': True,
            'profile_picture': 'default.jpg'
        }
        data['users'].append(admin_user)
        
        with open('users.json', 'w') as f:
            json.dump(data, f, indent=4)
        print('Admin user created successfully')
    else:
        print('Admin user already exists')
    
    print('Database initialized successfully')

if __name__ == '__main__':
    init_db() 