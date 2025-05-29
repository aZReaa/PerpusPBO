# Perpustakaan App

Aplikasi manajemen perpustakaan sekolah yang dibangun dengan Flask.

## Fitur

- **Admin Dashboard**: Kelola buku, member, peminjaman, dan denda
- **Member Dashboard**: Cari buku, lihat riwayat peminjaman, kelola profil
- **Responsive Design**: Tampilan yang optimal di desktop dan mobile
- **File Upload**: Upload gambar buku dan foto profil
- **Search & Filter**: Pencarian dan filter yang powerful
- **PostgreSQL Support**: Dukungan untuk database PostgreSQL di production
- **Environment Variables**: Konfigurasi mudah melalui environment variables
- **Secure Admin**: Password admin yang aman dengan environment variable

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render.com (Web Service + PostgreSQL)

## Deployment di Render

### Prerequisites

1. Akun GitHub
2. Akun Render (https://render.com)

### Langkah Deployment

1. **Push ke GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/username/perpustakaan-app.git
   git push -u origin main
   ```

2. **Deploy di Render**
   - Login ke Render.com
   - Klik "New +" dan pilih "Blueprint"
   - Connect repository GitHub Anda
   - Render akan otomatis mendeteksi `render.yaml` dan mengkonfigurasi:
     - Web Service (Flask app)
     - PostgreSQL Database
     - Environment variables

3. **Konfigurasi Otomatis**
   - Database PostgreSQL akan dibuat otomatis
   - Environment variables akan di-set:
     - `SECRET_KEY`: Auto-generated
     - `DATABASE_URL`: From PostgreSQL database
     - `PYTHON_VERSION`: 3.11.0

4. **Akses Aplikasi**
   - Admin default: username `admin`, password `admin123`
   - URL aplikasi akan tersedia setelah deployment selesai

### File Konfigurasi

- `render.yaml`: Konfigurasi utama Render
- `build.sh`: Script untuk inisialisasi database
- `Procfile`: Alternative untuk web service
- `requirements.txt`: Dependencies Python
- `.gitignore`: File yang diabaikan git

### Environment Variables

Aplikasi akan menggunakan environment variables berikut:

- `SECRET_KEY`: Key untuk session Flask (auto-generated di Render)
- `DATABASE_URL`: URL database PostgreSQL (auto-set oleh Render)
- `PYTHON_VERSION`: Versi Python yang digunakan

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run aplikasi
python app.py
```

Aplikasi akan berjalan di http://localhost:5000

### Production Notes

- File upload disimpan di local storage (untuk production yang serius, gunakan cloud storage seperti AWS S3)
- Database menggunakan PostgreSQL di production, SQLite di development
- Secret key auto-generated untuk keamanan

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: SQLite (dev), PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render.com
