"""
Database Migration Script for Perpustakaan App
This script helps migrate data from SQLite to PostgreSQL for deployment.

Usage:
1. Export data from SQLite (development):
   python migrate_data.py export

2. Import data to PostgreSQL (production):
   DATABASE_URL=your_postgres_url python migrate_data.py import
"""

import sys
import os
import json
from datetime import datetime
from app import app, db, User, Book, Category, Loan, Fine

# Helper function to serialize datetime objects
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def export_data():
    """Export all data from SQLite database to JSON files"""
    print("Exporting data from SQLite database...")
    
    with app.app_context():
        # Export users (except passwords)
        users = User.query.all()
        user_data = []
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nama_lengkap': user.nama_lengkap,
                'role': user.role,
                'kelas': user.kelas,
                'profile_pic': user.profile_pic,
                # password_hash is intentionally excluded for security
            }
            user_data.append(user_dict)
        
        # Export categories
        categories = Category.query.all()
        category_data = []
        for category in categories:
            category_dict = {
                'id': category.id,
                'nama': category.nama,
                'deskripsi': category.deskripsi
            }
            category_data.append(category_dict)
        
        # Export books
        books = Book.query.all()
        book_data = []
        for book in books:
            book_dict = {
                'id': book.id,
                'judul': book.judul,
                'penulis': book.penulis,
                'penerbit': book.penerbit,
                'tahun_terbit': book.tahun_terbit,
                'isbn': book.isbn,
                'stok': book.stok,
                'tersedia': book.tersedia,
                'category_id': book.category_id,
                'deskripsi': book.deskripsi,
                'cover_img': book.cover_img
            }
            book_data.append(book_dict)
        
        # Export loans
        loans = Loan.query.all()
        loan_data = []
        for loan in loans:
            loan_dict = {
                'id': loan.id,
                'user_id': loan.user_id,
                'book_id': loan.book_id,
                'tanggal_pinjam': loan.tanggal_pinjam,
                'tanggal_kembali': loan.tanggal_kembali,
                'status': loan.status
            }
            loan_data.append(loan_dict)
        
        # Export fines
        fines = Fine.query.all()
        fine_data = []
        for fine in fines:
            fine_dict = {
                'id': fine.id,
                'loan_id': fine.loan_id,
                'jumlah': fine.jumlah,
                'status': fine.status,
                'tanggal_pembayaran': fine.tanggal_pembayaran
            }
            fine_data.append(fine_dict)
    
    # Save to files
    os.makedirs('migration', exist_ok=True)
    with open('migration/users.json', 'w') as f:
        json.dump(user_data, f, default=json_serial, indent=2)
    
    with open('migration/categories.json', 'w') as f:
        json.dump(category_data, f, default=json_serial, indent=2)
    
    with open('migration/books.json', 'w') as f:
        json.dump(book_data, f, default=json_serial, indent=2)
    
    with open('migration/loans.json', 'w') as f:
        json.dump(loan_data, f, default=json_serial, indent=2)
    
    with open('migration/fines.json', 'w') as f:
        json.dump(fine_data, f, default=json_serial, indent=2)
    
    print("Data export complete! Files saved in the 'migration' folder.")
    print("IMPORTANT: Passwords were not exported for security reasons.")
    print("           Users will need to reset their passwords.")

def import_data():
    """Import data from JSON files to PostgreSQL database"""
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: DATABASE_URL environment variable is required for import!")
        print("Usage: DATABASE_URL=your_postgres_url python migrate_data.py import")
        return
    
    print("Importing data to PostgreSQL database...")
    
    if not os.path.exists('migration'):
        print("ERROR: Migration folder not found. Please run export first.")
        return
    
    with app.app_context():
        # Create all tables first
        db.create_all()
        
        # Import categories
        if os.path.exists('migration/categories.json'):
            with open('migration/categories.json', 'r') as f:
                categories = json.load(f)
                for category_data in categories:
                    category = Category(
                        id=category_data['id'],
                        nama=category_data['nama'],
                        deskripsi=category_data['deskripsi']
                    )
                    db.session.add(category)
            print(f"Imported {len(categories)} categories")
        
        # Import books
        if os.path.exists('migration/books.json'):
            with open('migration/books.json', 'r') as f:
                books = json.load(f)
                for book_data in books:
                    book = Book(
                        id=book_data['id'],
                        judul=book_data['judul'],
                        penulis=book_data['penulis'],
                        penerbit=book_data['penerbit'],
                        tahun_terbit=book_data['tahun_terbit'],
                        isbn=book_data['isbn'],
                        stok=book_data['stok'],
                        tersedia=book_data['tersedia'],
                        category_id=book_data['category_id'],
                        deskripsi=book_data['deskripsi'],
                        cover_img=book_data['cover_img']
                    )
                    db.session.add(book)
            print(f"Imported {len(books)} books")
        
        # Commit to save categories and books first
        db.session.commit()
        
        # Import users
        if os.path.exists('migration/users.json'):
            from werkzeug.security import generate_password_hash
            temp_password = 'ChangeMeNow!'  # Temporary password
            
            with open('migration/users.json', 'r') as f:
                users = json.load(f)
                for user_data in users:
                    # Skip admin user as it will be created by create_admin()
                    if user_data['username'] == 'admin':
                        continue
                    
                    user = User(
                        id=user_data['id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=generate_password_hash(temp_password),
                        nama_lengkap=user_data['nama_lengkap'],
                        role=user_data['role'],
                        kelas=user_data['kelas'],
                        profile_pic=user_data['profile_pic']
                    )
                    db.session.add(user)
            print(f"Imported {len(users)} users with temporary password: {temp_password}")
            
        # Import loans
        if os.path.exists('migration/loans.json'):
            with open('migration/loans.json', 'r') as f:
                loans = json.load(f)
                for loan_data in loans:
                    # Parse datetime strings
                    tanggal_pinjam = datetime.fromisoformat(loan_data['tanggal_pinjam'])
                    tanggal_kembali = None
                    if loan_data['tanggal_kembali']:
                        tanggal_kembali = datetime.fromisoformat(loan_data['tanggal_kembali'])
                    
                    loan = Loan(
                        id=loan_data['id'],
                        user_id=loan_data['user_id'],
                        book_id=loan_data['book_id'],
                        tanggal_pinjam=tanggal_pinjam,
                        tanggal_kembali=tanggal_kembali,
                        status=loan_data['status']
                    )
                    db.session.add(loan)
            print(f"Imported {len(loans)} loans")
        
        # Import fines
        if os.path.exists('migration/fines.json'):
            with open('migration/fines.json', 'r') as f:
                fines = json.load(f)
                for fine_data in fines:
                    # Parse datetime strings
                    tanggal_pembayaran = None
                    if fine_data['tanggal_pembayaran']:
                        tanggal_pembayaran = datetime.fromisoformat(fine_data['tanggal_pembayaran'])
                    
                    fine = Fine(
                        id=fine_data['id'],
                        loan_id=fine_data['loan_id'],
                        jumlah=fine_data['jumlah'],
                        status=fine_data['status'],
                        tanggal_pembayaran=tanggal_pembayaran
                    )
                    db.session.add(fine)
            print(f"Imported {len(fines)} fines")
        
        # Commit all changes
        db.session.commit()
        print("Data import complete!")
        print("IMPORTANT: All users (except admin) have been assigned a temporary password:", temp_password)
        print("           Please reset passwords through the admin interface.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_data.py [export|import]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    if command == "export":
        export_data()
    elif command == "import":
        import_data()
    else:
        print("Invalid command. Use 'export' or 'import'")
        sys.exit(1)
