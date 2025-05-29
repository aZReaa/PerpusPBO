# PowerShell build script for Render deployment

# Install Python dependencies
pip install -r requirements.txt

# Initialize database tables and create admin user
python -c "
from app import app, db, create_admin
with app.app_context():
    db.create_all()
    create_admin()
    print('Database initialized successfully!')
"
