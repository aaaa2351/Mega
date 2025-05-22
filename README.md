# File Sharing Application

A comprehensive file-sharing platform built with Python Flask, featuring user authentication, file management, points system, and admin panel.

## Features

- User Authentication
  - Email verification
  - Profile management
  - Points system
  - Premium user status

- File Management
  - Drag-and-drop file upload
  - File size limits (500MB for free users, unlimited for premium)
  - Points cost: 15 points per 10MB
  - 10-day file expiration
  - Secure file storage

- File Sharing
  - Generate shareable download links
  - Share files with specific users
  - Copy-to-clipboard functionality

- Admin Features
  - User management
  - System monitoring
  - Statistics dashboard

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd file-sharing-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your-secret-key-here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
GENERAL_ACCESS_PASSWORD=welcome123
```

5. Initialize the database:
```bash
python init_db.py
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Register a new account or login with existing credentials
2. Upload files using the drag-and-drop interface
3. Share files with other users or generate download links
4. Manage your profile and view statistics
5. For admin access, set `is_admin=True` in the database for your user

## Points System

- New users start with 400 points
- File upload costs: 15 points per 10MB
- Premium users get unlimited file size uploads
- Points can be earned through various activities (to be implemented)

## Security Features

- Password hashing
- Email verification
- Secure file handling
- Access control
- File expiration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 