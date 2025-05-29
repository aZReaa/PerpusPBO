from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration for production and development
if os.environ.get('DATABASE_URL'):
    # Production configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    # Log that we're in production mode
    print("Running in PRODUCTION mode")
else:
    # Development configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///perpustakaan.db'
    # Log that we're in development mode
    print("Running in DEVELOPMENT mode")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads/books')
PROFILE_FOLDER = os.environ.get('PROFILE_FOLDER', 'static/uploads/profiles')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Make sure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_FOLDER, exist_ok=True)

# Predefined class options for consistency
KELAS_OPTIONS = {
    'Kelas X': [
        ('X-IPA-1', 'X IPA 1'),
        ('X-IPA-2', 'X IPA 2'),
        ('X-IPA-3', 'X IPA 3'),
        ('X-IPS-1', 'X IPS 1'),
        ('X-IPS-2', 'X IPS 2'),
        ('X-IPS-3', 'X IPS 3'),
    ],
    'Kelas XI': [
        ('XI-IPA-1', 'XI IPA 1'),
        ('XI-IPA-2', 'XI IPA 2'),
        ('XI-IPA-3', 'XI IPA 3'),
        ('XI-IPS-1', 'XI IPS 1'),
        ('XI-IPS-2', 'XI IPS 2'),
        ('XI-IPS-3', 'XI IPS 3'),
    ],
    'Kelas XII': [
        ('XII-IPA-1', 'XII IPA 1'),
        ('XII-IPA-2', 'XII IPA 2'),
        ('XII-IPA-3', 'XII IPA 3'),
        ('XII-IPS-1', 'XII IPS 1'),
        ('XII-IPS-2', 'XII IPS 2'),
        ('XII-IPS-3', 'XII IPS 3'),
    ]
}

def get_kelas_options():
    """Return flattened list of all class options for validation"""
    options = []
    for group_name, group_options in KELAS_OPTIONS.items():
        options.extend([option[0] for option in group_options])
    return options

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_book_image(file):
    """Save uploaded book image and return the file path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create unique filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return f'uploads/books/{filename}'
    return None

def save_profile_photo(file):
    """Save uploaded profile photo and return the file path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create unique filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(app.config['PROFILE_FOLDER'], filename)
        file.save(file_path)
        return f'uploads/profiles/{filename}'
    return None

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # 'admin' or 'member'
    nama_lengkap = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(20))  # untuk member
    profile_photo = db.Column(db.String(200))  # path to profile photo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def active_loans_count(self):
        """Return the count of active loans for this user"""
        if self.role != 'member':
            return 0
        return Peminjaman.query.filter_by(user_id=self.id, status='dipinjam').count()
    
    def due_soon_count(self):
        """Return the count of loans due within 2 days for this user"""
        if self.role != 'member':
            return 0
        from datetime import date, timedelta
        due_soon_date = date.today() + timedelta(days=2)
        return Peminjaman.query.filter(
            Peminjaman.user_id == self.id,
            Peminjaman.status == 'dipinjam',
            Peminjaman.tanggal_kembali_rencana <= due_soon_date
        ).count()

class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    pengarang = db.Column(db.String(100), nullable=False)
    penerbit = db.Column(db.String(100))
    tahun_terbit = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    kategori = db.Column(db.String(50))
    stok = db.Column(db.Integer, default=1)
    deskripsi = db.Column(db.Text)
    gambar = db.Column(db.String(200))  # path to book cover image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Peminjaman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buku_id = db.Column(db.Integer, db.ForeignKey('buku.id'), nullable=False)
    tanggal_pinjam = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_kembali_rencana = db.Column(db.DateTime, nullable=False)
    tanggal_kembali_aktual = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='dipinjam')  # 'dipinjam', 'dikembalikan'
    denda = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref='peminjaman')
    buku = db.relationship('Buku', backref='peminjaman')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_kelas_options():
    """Make KELAS_OPTIONS available to all templates"""
    return dict(KELAS_OPTIONS=KELAS_OPTIONS)

@app.route('/')
def index():
    # Redirect to login since this is the main entry point
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('member_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('member_dashboard'))
        else:
            flash('Username atau password salah!')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        nama_lengkap = request.form['nama_lengkap']
        kelas = request.form['kelas']
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan!')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            nama_lengkap=nama_lengkap,
            kelas=kelas,
            role='member'
        )
        
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    total_buku = Buku.query.count()
    total_member = User.query.filter_by(role='member').count()
    total_peminjaman_aktif = Peminjaman.query.filter_by(status='dipinjam').count()
    
    # Calculate due today and overdue
    today = datetime.utcnow().date()
    due_today = Peminjaman.query.filter(
        Peminjaman.status == 'dipinjam',
        db.func.date(Peminjaman.tanggal_kembali_rencana) == today
    ).count()
    
    overdue = Peminjaman.query.filter(
        Peminjaman.status == 'dipinjam',
        Peminjaman.tanggal_kembali_rencana < datetime.utcnow()
    ).count()
      # Calculate accuracy rate
    total_returns = Peminjaman.query.filter_by(status='dikembalikan').count()
    on_time_returns = Peminjaman.query.filter(
        Peminjaman.status == 'dikembalikan',
        Peminjaman.tanggal_kembali_aktual <= Peminjaman.tanggal_kembali_rencana
    ).count()
    accuracy_rate = (on_time_returns / total_returns * 100) if total_returns > 0 else 100
    
    return render_template('admin/dashboard.html', 
                         total_books=total_buku,
                         total_members=total_member,
                         total_peminjaman_aktif=total_peminjaman_aktif,
                         due_today=due_today,
                         overdue=overdue,
                         accuracy_rate=round(accuracy_rate, 1))

@app.route('/member/dashboard')
@login_required
def member_dashboard():
    if current_user.role != 'member':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    peminjaman_aktif = Peminjaman.query.filter_by(user_id=current_user.id, status='dipinjam').all()
    
    # Calculate due soon count (books due within 2 days)
    today = datetime.now().date()
    due_soon_date = today + timedelta(days=2)
    due_soon_count = Peminjaman.query.filter(
        Peminjaman.user_id == current_user.id,
        Peminjaman.status == 'dipinjam',
        Peminjaman.tanggal_kembali_rencana.between(today, due_soon_date)
    ).count()
    
    # Calculate total unpaid fines
    total_denda = db.session.query(db.func.sum(Peminjaman.denda)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    
    # Get recent books (newest additions) with available stock
    recent_books = Buku.query.filter(Buku.stok > 0).order_by(Buku.created_at.desc()).limit(6).all()
    
    return render_template('member/dashboard.html', 
                         peminjaman_aktif=peminjaman_aktif,
                         recent_books=recent_books,
                         today=today,
                         due_soon_count=due_soon_count,
                         total_denda=total_denda)

@app.route('/admin/books')
@login_required
def admin_books():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    kategori = request.args.get('kategori', '')
    pengarang = request.args.get('pengarang', '')
    tahun = request.args.get('tahun', '')
    
    query = Buku.query
    
    if search:
        query = query.filter(
            (Buku.judul.contains(search)) | 
            (Buku.pengarang.contains(search)) |
            (Buku.penerbit.contains(search)) |
            (Buku.isbn.contains(search))
        )
    
    if kategori:
        query = query.filter_by(kategori=kategori)
    
    if pengarang:
        query = query.filter_by(pengarang=pengarang)
    
    if tahun:
        query = query.filter_by(tahun_terbit=int(tahun))
    
    books = query.all()
    
    # Get available filter options
    categories = db.session.query(Buku.kategori).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    pengarang_list = db.session.query(Buku.pengarang).distinct().order_by(Buku.pengarang).all()
    pengarang_list = [p[0] for p in pengarang_list if p[0]]
    
    tahun_list = db.session.query(Buku.tahun_terbit).distinct().order_by(Buku.tahun_terbit.desc()).all()
    tahun_list = [t[0] for t in tahun_list if t[0]]
    
    return render_template('admin/books.html', 
                         books=books,
                         categories=categories,
                         pengarang_list=pengarang_list,
                         tahun_list=tahun_list,
                         search=search,
                         selected_kategori=kategori,
                         selected_pengarang=pengarang,
                         selected_tahun=tahun)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def admin_add_book():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        judul = request.form['judul']
        pengarang = request.form['pengarang']
        penerbit = request.form['penerbit']
        tahun_terbit = int(request.form['tahun_terbit'])
        isbn = request.form['isbn']
        kategori = request.form['kategori']
        stok = int(request.form['stok'])
        deskripsi = request.form['deskripsi']
        
        # Check if ISBN already exists
        if Buku.query.filter_by(isbn=isbn).first():
            flash('ISBN sudah ada!')
            return render_template('admin/add_book.html')
        
        # Handle file upload
        file = request.files.get('gambar')
        gambar_path = save_book_image(file)  # Save image and get file path
        
        book = Buku(
            judul=judul,
            pengarang=pengarang,
            penerbit=penerbit,
            tahun_terbit=tahun_terbit,
            isbn=isbn,
            kategori=kategori,
            stok=stok,
            deskripsi=deskripsi,
            gambar=gambar_path  # Save file path to database
        )
        
        db.session.add(book)
        db.session.commit()
        flash('Buku berhasil ditambahkan!')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/add_book.html')

@app.route('/admin/books/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_book(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    book = Buku.query.get_or_404(id)
    
    if request.method == 'POST':
        book.judul = request.form['judul']
        book.pengarang = request.form['pengarang']
        book.penerbit = request.form['penerbit']
        book.tahun_terbit = int(request.form['tahun_terbit'])
        book.isbn = request.form['isbn']
        book.kategori = request.form['kategori']
        book.stok = int(request.form['stok'])
        book.deskripsi = request.form['deskripsi']
        
        # Handle file upload
        file = request.files.get('gambar')
        if file:
            gambar_path = save_book_image(file)  # Save new image and get file path
            book.gambar = gambar_path  # Update file path in database
        
        db.session.commit()
        flash('Buku berhasil diperbarui!')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/edit_book.html', book=book)

@app.route('/admin/books/delete/<int:id>')
@login_required
def admin_delete_book(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    book = Buku.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Buku berhasil dihapus!')
    return redirect(url_for('admin_books'))

@app.route('/admin/members')
@login_required
def admin_members():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    members = User.query.filter_by(role='member').all()
    
    # Calculate total active loans for statistics
    total_active_loans = Peminjaman.query.filter_by(status='dipinjam').count()
    
    return render_template('admin/members.html', 
                         members=members, 
                         total_active_loans=total_active_loans)

@app.route('/admin/members/add', methods=['GET', 'POST'])
@login_required
def admin_add_member():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        nama_lengkap = request.form['nama_lengkap']
        kelas = request.form['kelas']
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!')
            return render_template('admin/add_member.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan!')
            return render_template('admin/add_member.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            nama_lengkap=nama_lengkap,
            kelas=kelas,
            role='member'
        )
        
        db.session.add(user)
        db.session.commit()
        flash('Member berhasil ditambahkan!')
        return redirect(url_for('admin_members'))
    
    return render_template('admin/add_member.html')

@app.route('/admin/members/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_member(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    member = User.query.get_or_404(id)
    
    if member.role != 'member':
        flash('Tidak dapat mengedit user admin!')
        return redirect(url_for('admin_members'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        nama_lengkap = request.form['nama_lengkap']
        kelas = request.form['kelas']
        password = request.form.get('password')
        
        # Check if username already exists (excluding current member)
        existing_user = User.query.filter(User.username == username, User.id != id).first()
        if existing_user:
            flash('Username sudah digunakan!')
            return render_template('admin/edit_member.html', member=member)
        
        # Check if email already exists (excluding current member)
        existing_email = User.query.filter(User.email == email, User.id != id).first()
        if existing_email:
            flash('Email sudah digunakan!')
            return render_template('admin/edit_member.html', member=member)
        
        # Update member data
        member.username = username
        member.email = email
        member.nama_lengkap = nama_lengkap
        member.kelas = kelas
        
        # Update password if provided
        if password:
            member.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash('Member berhasil diperbarui!')
        return redirect(url_for('admin_members'))
    
    return render_template('admin/edit_member.html', member=member)

@app.route('/admin/members/delete/<int:id>')
@login_required
def admin_delete_member(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    member = User.query.get_or_404(id)
    
    if member.role != 'member':
        flash('Tidak dapat menghapus user admin!')
        return redirect(url_for('admin_members'))
    
    # Check if member has active loans
    active_loans = Peminjaman.query.filter_by(user_id=member.id, status='dipinjam').count()
    if active_loans > 0:
        flash(f'Tidak dapat menghapus member karena masih memiliki {active_loans} peminjaman aktif!')
        return redirect(url_for('admin_members'))
    
    # Delete all loan history for this member
    Peminjaman.query.filter_by(user_id=member.id).delete()
    
    # Delete member
    db.session.delete(member)
    db.session.commit()
    
    flash('Member berhasil dihapus!')
    return redirect(url_for('admin_members'))

@app.route('/admin/members/<int:id>/loans')
@login_required
def admin_member_loans(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    member = User.query.get_or_404(id)
    
    if member.role != 'member':
        flash('User bukan member!')
        return redirect(url_for('admin_members'))
    
    loans = Peminjaman.query.filter_by(user_id=member.id).order_by(Peminjaman.tanggal_pinjam.desc()).all()
    
    return render_template('admin/member_loans.html', member=member, loans=loans)

@app.route('/admin/loans')
@login_required
def admin_loans():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    # Get filter parameter from URL
    filter_type = request.args.get('filter', 'all')
      # Base query
    loans_query = Peminjaman.query
      # Apply filters based on the filter_type
    if filter_type == 'pending':
        loans_query = loans_query.filter(Peminjaman.status == 'menunggu_konfirmasi')
    elif filter_type == 'due_today':
        from datetime import date
        today = date.today()
        loans_query = loans_query.filter(
            Peminjaman.status == 'dipinjam',
            Peminjaman.tanggal_kembali_rencana == today
        )
    elif filter_type == 'overdue':
        from datetime import date
        today = date.today()
        loans_query = loans_query.filter(
            Peminjaman.status == 'dipinjam',
            Peminjaman.tanggal_kembali_rencana < today
        )
    elif filter_type == 'active':
        loans_query = loans_query.filter(Peminjaman.status == 'dipinjam')
    
    loans = loans_query.order_by(Peminjaman.tanggal_pinjam.desc()).all()
    
    # Calculate statistics for display
    today = datetime.utcnow().date()
    pending_count = Peminjaman.query.filter_by(status='menunggu_konfirmasi').count()
    overdue_count = Peminjaman.query.filter(
        Peminjaman.status == 'dipinjam',
        Peminjaman.tanggal_kembali_rencana < datetime.utcnow()
    ).count()
    due_today_count = Peminjaman.query.filter(
        Peminjaman.status == 'dipinjam',
        db.func.date(Peminjaman.tanggal_kembali_rencana) == today
    ).count()
    
    return render_template('admin/loans.html', 
                         loans=loans,
                         today=today,
                         pending_count=pending_count,
                         overdue_count=overdue_count,
                         due_today_count=due_today_count)

@app.route('/admin/loans/process', methods=['GET', 'POST'])
@login_required
def admin_process_loan():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        buku_id = int(request.form['buku_id'])
        
        user = User.query.get(user_id)
        buku = Buku.query.get(buku_id)
        
        if not user or not buku:
            flash('User atau buku tidak ditemukan!')
            return redirect(url_for('admin_process_loan'))
        
        if buku.stok <= 0:
            flash('Stok buku tidak tersedia!')
            return redirect(url_for('admin_process_loan'))
        
        # Check if user already borrowed this book
        existing_loan = Peminjaman.query.filter_by(
            user_id=user_id, 
            buku_id=buku_id, 
            status='dipinjam'
        ).first()
        
        if existing_loan:
            flash('User sudah meminjam buku ini!')
            return redirect(url_for('admin_process_loan'))
          # Check if confirmation process is required
        confirmation_required = request.form.get('confirmation_required', 'no')
        
        if confirmation_required == 'yes':
            # Create pending loan
            loan = Peminjaman(
                user_id=user_id,
                buku_id=buku_id,
                status='menunggu_konfirmasi',
                tanggal_kembali_rencana=datetime.utcnow() + timedelta(days=7)
            )
            
            db.session.add(loan)
            db.session.commit()
            flash('Peminjaman berhasil dicatat dan menunggu konfirmasi!')
        else:
            # Direct loan process
            loan = Peminjaman(
                user_id=user_id,
                buku_id=buku_id,
                tanggal_kembali_rencana=datetime.utcnow() + timedelta(days=7)
            )
            
            buku.stok -= 1
            
            db.session.add(loan)
            db.session.commit()
            flash('Peminjaman berhasil diproses!')
            
        return redirect(url_for('admin_loans'))
    
    users = User.query.filter_by(role='member').all()
    books = Buku.query.filter(Buku.stok > 0).all()
    return render_template('admin/process_loan.html', users=users, books=books)

@app.route('/admin/loans/return/<int:id>')
@login_required
def admin_return_book(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    loan = Peminjaman.query.get_or_404(id)
    
    if loan.status == 'dikembalikan':
        flash('Buku sudah dikembalikan!')
        return redirect(url_for('admin_loans'))
    
    loan.status = 'dikembalikan'
    loan.tanggal_kembali_aktual = datetime.utcnow()
    
    # Calculate fine if late
    if loan.tanggal_kembali_aktual > loan.tanggal_kembali_rencana:
        days_late = (loan.tanggal_kembali_aktual - loan.tanggal_kembali_rencana).days
        loan.denda = days_late * 1000  # Rp 1000 per day
    
    # Return stock
    buku = Buku.query.get(loan.buku_id)
    buku.stok += 1
    
    db.session.commit()
    flash('Buku berhasil dikembalikan!')
    return redirect(url_for('admin_loans'))

@app.route('/admin/books/search')
@login_required
def admin_search_books():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    kategori = request.args.get('kategori', '')
    pengarang = request.args.get('pengarang', '')
    tahun = request.args.get('tahun', '')
    
    query = Buku.query
    
    if search:
        query = query.filter(
            (Buku.judul.contains(search)) | 
            (Buku.pengarang.contains(search)) |
            (Buku.penerbit.contains(search)) |
            (Buku.isbn.contains(search))
        )
    
    if kategori:
        query = query.filter_by(kategori=kategori)
    
    if pengarang:
        query = query.filter_by(pengarang=pengarang)
    
    if tahun:
        query = query.filter_by(tahun_terbit=int(tahun))
    
    books = query.all()
    
    # Get available filter options
    categories = db.session.query(Buku.kategori).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    pengarang_list = db.session.query(Buku.pengarang).distinct().order_by(Buku.pengarang).all()
    pengarang_list = [p[0] for p in pengarang_list if p[0]]
    
    tahun_list = db.session.query(Buku.tahun_terbit).distinct().order_by(Buku.tahun_terbit.desc()).all()
    tahun_list = [t[0] for t in tahun_list if t[0]]
    
    return render_template('admin/search_books.html', 
                         books=books, 
                         categories=categories,
                         pengarang_list=pengarang_list,
                         tahun_list=tahun_list,
                         search=search,
                         selected_kategori=kategori,
                         selected_pengarang=pengarang,
                         selected_tahun=tahun)

@app.route('/member/books')
@login_required
def member_books():
    if current_user.role != 'member':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    kategori = request.args.get('kategori', '')
    pengarang = request.args.get('pengarang', '')
    tahun = request.args.get('tahun', '')
    
    query = Buku.query
    
    if search:
        query = query.filter(
            (Buku.judul.contains(search)) | 
            (Buku.pengarang.contains(search)) |
            (Buku.penerbit.contains(search))
        )
    
    if kategori:
        query = query.filter_by(kategori=kategori)
    
    if pengarang:
        query = query.filter_by(pengarang=pengarang)
    
    if tahun:
        query = query.filter_by(tahun_terbit=int(tahun))
    
    books = query.all()
    
    # Get available filter options
    categories = db.session.query(Buku.kategori).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    pengarang_list = db.session.query(Buku.pengarang).distinct().order_by(Buku.pengarang).all()
    pengarang_list = [p[0] for p in pengarang_list if p[0]]
    
    tahun_list = db.session.query(Buku.tahun_terbit).distinct().order_by(Buku.tahun_terbit.desc()).all()
    tahun_list = [t[0] for t in tahun_list if t[0]]
    
    return render_template('member/books.html', 
                         books=books, 
                         categories=categories,
                         pengarang_list=pengarang_list,
                         tahun_list=tahun_list,
                         search=search,
                         selected_kategori=kategori,
                         selected_pengarang=pengarang,
                         selected_tahun=tahun)

@app.route('/member/book/<int:id>')
@login_required
def member_book_detail(id):
    if current_user.role != 'member':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    book = Buku.query.get_or_404(id)
    
    # Check if user already borrowed this book
    existing_loan = Peminjaman.query.filter_by(
        user_id=current_user.id,
        buku_id=book.id,
        status='dipinjam'
    ).first()
    
    return render_template('member/book_detail.html', 
                         book=book, 
                         already_borrowed=existing_loan is not None)

@app.route('/member/borrow/<int:id>')
@login_required
def member_borrow_book(id):
    if current_user.role != 'member':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    book = Buku.query.get_or_404(id)
    
    # Check stock
    if book.stok <= 0:
        flash('Maaf, buku tidak tersedia!')
        return redirect(url_for('member_book_detail', id=id))
    
    # Check if user already borrowed this book
    existing_loan = Peminjaman.query.filter_by(
        user_id=current_user.id,
        buku_id=book.id,
        status='dipinjam'
    ).first()
    
    if existing_loan:
        flash('Anda sudah meminjam buku ini!')
        return redirect(url_for('member_book_detail', id=id))
    
    # Check if user has too many active loans (max 3)
    active_loans = Peminjaman.query.filter_by(
        user_id=current_user.id,
        status='dipinjam'
    ).count()
    
    if active_loans >= 3:
        flash('Anda sudah mencapai batas maksimum peminjaman (3 buku)!')
        return redirect(url_for('member_book_detail', id=id))
    
    # Create loan
    loan = Peminjaman(
        user_id=current_user.id,
        buku_id=book.id,
        tanggal_kembali_rencana=datetime.utcnow() + timedelta(days=7)
    )
    
    book.stok -= 1
    
    db.session.add(loan)
    db.session.commit()
    
    flash('Buku berhasil dipinjam! Batas pengembalian: ' + 
          loan.tanggal_kembali_rencana.strftime('%d/%m/%Y'))
    return redirect(url_for('member_dashboard'))

@app.route('/member/loans')
@login_required
def member_loans():
    if current_user.role != 'member':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    loans = Peminjaman.query.filter_by(user_id=current_user.id).order_by(Peminjaman.tanggal_pinjam.desc()).all()
    today = datetime.now().date()
    return render_template('member/loans.html', loans=loans, today=today)

@app.route('/member/profile')
@login_required
def member_profile():
    if current_user.role != 'member':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    user_loans = Peminjaman.query.filter_by(user_id=current_user.id).all()
    total_fines = db.session.query(db.func.sum(Peminjaman.denda)).filter_by(user_id=current_user.id).scalar() or 0
    
    return render_template('member/profile.html', 
                         user_loans=user_loans,
                         total_fines=total_fines)

@app.route('/member/profile/edit', methods=['GET', 'POST'])
@login_required
def member_edit_profile():
    if current_user.role != 'member':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        nama_lengkap = request.form['nama_lengkap']
        kelas = request.form['kelas']
        password = request.form.get('password')
        
        # Check if username already exists (excluding current user)
        existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
        if existing_user:
            flash('Username sudah digunakan!')
            return render_template('member/edit_profile.html')
        
        # Update profile data
        current_user.username = username
        current_user.nama_lengkap = nama_lengkap
        current_user.kelas = kelas
        
        # Update password if provided
        if password:
            current_user.password_hash = generate_password_hash(password)
        
        # Handle profile photo upload
        file = request.files.get('profile_photo')
        if file:
            profile_path = save_profile_photo(file)
            if profile_path:
                current_user.profile_photo = profile_path
        
        db.session.commit()
        flash('Profil berhasil diperbarui!')
        return redirect(url_for('member_profile'))
    
    return render_template('member/edit_profile.html')

def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_user = User(
            username='admin',
            email='admin@perpus.com',
            password_hash=generate_password_hash(admin_password),
            nama_lengkap='Administrator',
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user created: username=admin, password={'*' * len(admin_password)}")

@app.route('/admin/loans/confirm', methods=['GET', 'POST'])
@login_required
def admin_confirm_loan():
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        buku_id = int(request.form['buku_id'])
        
        user = User.query.get(user_id)
        buku = Buku.query.get(buku_id)
        
        if not user or not buku:
            flash('User atau buku tidak ditemukan!')
            return redirect(url_for('admin_loans'))
        
        if buku.stok <= 0:
            flash('Stok buku tidak tersedia!')
            return redirect(url_for('admin_loans'))
        
        # Check if user already borrowed this book
        existing_loan = Peminjaman.query.filter_by(
            user_id=user_id, 
            buku_id=buku_id, 
            status='dipinjam'
        ).first()
        
        if existing_loan:
            flash('User sudah meminjam buku ini!')
            return redirect(url_for('admin_loans'))
        
        loan = Peminjaman(
            user_id=user_id,
            buku_id=buku_id,
            status='menunggu_konfirmasi',
            tanggal_kembali_rencana=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(loan)
        db.session.commit()
        flash('Peminjaman berhasil dicatat dan menunggu konfirmasi!')
        return redirect(url_for('admin_loans'))
    
    users = User.query.filter_by(role='member').all()
    books = Buku.query.filter(Buku.stok > 0).all()
    return render_template('admin/confirm_loan.html', users=users, books=books)

@app.route('/admin/loans/approve/<int:id>')
@login_required
def admin_approve_loan(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    loan = Peminjaman.query.get_or_404(id)
    
    if loan.status != 'menunggu_konfirmasi':
        flash('Status peminjaman tidak valid untuk konfirmasi!')
        return redirect(url_for('admin_loans'))
    
    # Update loan status
    loan.status = 'dipinjam'
    
    # Reduce book stock
    buku = Buku.query.get(loan.buku_id)
    if buku.stok <= 0:
        flash('Stok buku tidak tersedia!')
        return redirect(url_for('admin_loans'))
    
    buku.stok -= 1
    
    db.session.commit()
    flash('Peminjaman berhasil dikonfirmasi!')
    return redirect(url_for('admin_loans'))

@app.route('/admin/loans/reject/<int:id>')
@login_required
def admin_reject_loan(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    loan = Peminjaman.query.get_or_404(id)
    
    if loan.status != 'menunggu_konfirmasi':
        flash('Status peminjaman tidak valid untuk penolakan!')
        return redirect(url_for('admin_loans'))
    
    # Delete the loan record
    db.session.delete(loan)
    db.session.commit()
    flash('Peminjaman berhasil ditolak!')
    return redirect(url_for('admin_loans'))

@app.route('/admin/loans/edit_fine/<int:id>', methods=['POST'])
@login_required
def admin_edit_fine(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    loan = Peminjaman.query.get_or_404(id)
    
    try:
        new_fine = int(request.form['denda'])
        if new_fine < 0:
            flash('Denda tidak boleh negatif!')
            return redirect(url_for('admin_loans'))
        
        loan.denda = new_fine
        db.session.commit()
        flash(f'Denda berhasil diubah menjadi Rp {new_fine:,}!')
    except ValueError:
        flash('Format denda tidak valid!')
    
    return redirect(url_for('admin_loans'))

@app.route('/admin/loans/delete_fine/<int:id>')
@login_required
def admin_delete_fine(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    loan = Peminjaman.query.get_or_404(id)
    loan.denda = 0
    db.session.commit()
    flash('Denda berhasil dihapus!')
    return redirect(url_for('admin_loans'))

@app.route('/admin/loans/calculate_fine/<int:id>')
@login_required
def admin_calculate_fine(id):
    if current_user.role != 'admin':
        flash('Akses ditolak!')
        return redirect(url_for('index'))
    
    loan = Peminjaman.query.get_or_404(id)
    
    if loan.status == 'dipinjam':
        # Calculate fine for overdue loans
        today = datetime.utcnow()
        if today > loan.tanggal_kembali_rencana:
            days_late = (today - loan.tanggal_kembali_rencana).days
            loan.denda = days_late * 1000  # Rp 1000 per day
            db.session.commit()
            flash(f'Denda dihitung: {days_late} hari × Rp 1.000 = Rp {loan.denda:,}')
        else:
            flash('Buku belum melewati batas waktu!')
    else:        flash('Hanya bisa menghitung denda untuk peminjaman aktif!')
    
    return redirect(url_for('admin_loans'))

@app.route('/admin/loans/calculate_all_fines', methods=['POST'])
@login_required
def admin_calculate_all_fines():
    if current_user.role != 'admin':
        return {'error': 'Akses ditolak!'}, 403
    
    try:
        # Get all active loans that are overdue
        today = datetime.utcnow()
        overdue_loans = Peminjaman.query.filter(
            Peminjaman.status == 'dipinjam',
            Peminjaman.tanggal_kembali_rencana < today,
            Peminjaman.denda == 0  # Only calculate if no fine exists yet
        ).all()
        
        calculated_count = 0
        total_fines = 0
        
        for loan in overdue_loans:
            days_late = (today - loan.tanggal_kembali_rencana).days
            fine_amount = days_late * 1000  # Rp 1000 per day
            loan.denda = fine_amount
            calculated_count += 1
            total_fines += fine_amount
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Berhasil menghitung denda untuk {calculated_count} peminjaman',
            'calculated_count': calculated_count,
            'total_fines': total_fines
        }
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
