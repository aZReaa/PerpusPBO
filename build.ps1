# PowerShell build script for Render deployment

# Install Python dependencies
pip install -r requirements.txt

# Initialize database tables and create admin user
python -c "
from app import app, db, create_admin
import os

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Create admin user
    create_admin()
    
    # Print success messages
    print('Database initialized successfully!')
    print(f'Admin username: admin')
    print(f'Admin password: {os.environ.get(\"ADMIN_PASSWORD\", \"admin123\")}')
    
    # Print database connection info (masked)
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url:
        masked_url = db_url[:15] + '****' + db_url[-10:] if len(db_url) > 30 else '****'
        print(f'Connected to database: {masked_url}')
    else:
        print('Using SQLite database for development')
"
