#!/usr/bin/env python3
"""
Script untuk membuat data test peminjaman yang terlambat
untuk menguji fitur Kelola Denda
"""

from app import app, db, User, Buku, Peminjaman
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def create_test_data():
    with app.app_context():
        print("🔄 Membuat data test untuk fitur Kelola Denda...")
        
        # Cek apakah sudah ada user test
        test_user = User.query.filter_by(username='siswa_test').first()
        if not test_user:
            # Buat user test
            test_user = User(
                username='siswa_test',
                email='siswa.test@email.com',
                password_hash=generate_password_hash('password123'),
                nama_lengkap='Siswa Test Denda',
                kelas='XII-IPA-1',
                role='member'
            )
            db.session.add(test_user)
            print("✅ User test 'siswa_test' berhasil dibuat")
        else:
            print("ℹ️  User test 'siswa_test' sudah ada")
        
        # Cek apakah sudah ada buku test
        test_book = Buku.query.filter_by(isbn='TEST-OVERDUE-001').first()
        if not test_book:
            # Buat buku test
            test_book = Buku(
                judul='Buku Test Keterlambatan',
                pengarang='Penulis Test',
                penerbit='Penerbit Test',
                tahun_terbit=2024,
                isbn='TEST-OVERDUE-001',
                kategori='Test',
                stok=5,
                deskripsi='Buku untuk test fitur denda keterlambatan'
            )
            db.session.add(test_book)
            print("✅ Buku test berhasil dibuat")
        else:
            print("ℹ️  Buku test sudah ada")
        
        db.session.commit()
        
        # Hapus peminjaman test yang sudah ada untuk user ini
        existing_loans = Peminjaman.query.filter_by(user_id=test_user.id).all()
        for loan in existing_loans:
            db.session.delete(loan)
        
        # Buat beberapa peminjaman yang terlambat dengan durasi berbeda
        test_loans = [
            {
                'days_overdue': 5,
                'description': '5 hari terlambat (denda: Rp 5.000)'
            },
            {
                'days_overdue': 10,
                'description': '10 hari terlambat (denda: Rp 10.000)'
            },
            {
                'days_overdue': 1,
                'description': '1 hari terlambat (denda: Rp 1.000)'
            }
        ]
        
        today = datetime.now()
        
        for i, loan_data in enumerate(test_loans):
            days_overdue = loan_data['days_overdue']
            
            # Tanggal pinjam: 14 hari yang lalu (durasi standar)
            tanggal_pinjam = today - timedelta(days=14)
            
            # Tanggal kembali rencana: 7 hari setelah pinjam (sudah lewat beberapa hari)
            tanggal_kembali_rencana = tanggal_pinjam + timedelta(days=7)
            
            # Pastikan tanggal kembali rencana sudah lewat sesuai days_overdue
            if (today.date() - tanggal_kembali_rencana.date()).days < days_overdue:
                # Adjust tanggal kembali rencana agar sesuai dengan days_overdue
                tanggal_kembali_rencana = today - timedelta(days=days_overdue)
                tanggal_pinjam = tanggal_kembali_rencana - timedelta(days=7)
            
            # Hitung denda otomatis (Rp 1000 per hari)
            denda = days_overdue * 1000
            
            loan = Peminjaman(
                user_id=test_user.id,
                buku_id=test_book.id,
                tanggal_pinjam=tanggal_pinjam,
                tanggal_kembali_rencana=tanggal_kembali_rencana,
                status='dipinjam',
                denda=denda
            )
            
            db.session.add(loan)
            print(f"✅ Peminjaman test #{i+1} dibuat: {loan_data['description']}")
        
        # Buat juga 1 peminjaman yang jatuh tempo hari ini
        today_loan = Peminjaman(
            user_id=test_user.id,
            buku_id=test_book.id,
            tanggal_pinjam=today - timedelta(days=7),
            tanggal_kembali_rencana=today,  # Jatuh tempo hari ini
            status='dipinjam',
            denda=0
        )
        db.session.add(today_loan)
        print("✅ Peminjaman yang jatuh tempo hari ini dibuat")
        
        # Buat 1 peminjaman normal (belum jatuh tempo)
        future_loan = Peminjaman(
            user_id=test_user.id,
            buku_id=test_book.id,
            tanggal_pinjam=today - timedelta(days=2),
            tanggal_kembali_rencana=today + timedelta(days=5),  # Jatuh tempo 5 hari lagi
            status='dipinjam',
            denda=0
        )
        db.session.add(future_loan)
        print("✅ Peminjaman normal (belum jatuh tempo) dibuat")
        
        db.session.commit()
        
        print("\n🎉 Data test berhasil dibuat!")
        print("\n📋 Detail data test:")
        print("👤 Username: siswa_test")
        print("🔐 Password: password123")
        print("📚 Total peminjaman test: 5 (3 terlambat, 1 jatuh tempo hari ini, 1 normal)")
        print("\n🚀 Silakan login sebagai admin dan cek halaman 'Kelola Peminjaman'")
        print("💡 Gunakan filter 'Terlambat' untuk melihat peminjaman yang terlambat")
        print("🔧 Klik tombol 'Kelola Denda' untuk menguji fitur modal")

if __name__ == '__main__':
    create_test_data()
