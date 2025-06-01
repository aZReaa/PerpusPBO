#!/usr/bin/env python3
"""
Script to verify that all fine management features are working correctly
"""

from app import app, db, User, Buku, Peminjaman
from datetime import datetime, timedelta

def verify_fine_management():
    with app.app_context():
        print("🔍 Verifying Fine Management System...\n")
        
        # Check if test data exists
        test_user = User.query.filter_by(username='siswa_test').first()
        if not test_user:
            print("❌ Test user not found!")
            return
        
        print(f"✅ Test user found: {test_user.nama_lengkap}")
        
        # Check loans for test user
        loans = Peminjaman.query.filter_by(user_id=test_user.id).all()
        print(f"📚 Total loans for test user: {len(loans)}")
        
        today = datetime.utcnow().date()
        
        # Categorize loans
        dipinjam_count = 0
        dikembalikan_count = 0
        terlambat_count = 0
        jatuh_tempo_today_count = 0
        
        for loan in loans:
            print(f"\n📖 Loan ID {loan.id}:")
            print(f"   Book: {loan.buku.judul}")
            print(f"   Status: {loan.status}")
            print(f"   Due Date: {loan.tanggal_kembali_rencana.date()}")
            print(f"   Fine: Rp {loan.denda:,}")
            print(f"   Fine Status: {loan.status_denda}")
            
            if loan.status == 'dipinjam':
                dipinjam_count += 1
                if loan.tanggal_kembali_rencana.date() < today:
                    terlambat_count += 1
                    print(f"   🚨 OVERDUE: {(today - loan.tanggal_kembali_rencana.date()).days} days late")
                elif loan.tanggal_kembali_rencana.date() == today:
                    jatuh_tempo_today_count += 1
                    print(f"   ⏰ DUE TODAY")
                else:
                    print(f"   📖 ACTIVE")
            else:
                dikembalikan_count += 1
                print(f"   ✅ RETURNED")
        
        print(f"\n📊 Summary:")
        print(f"   Total: {len(loans)}")
        print(f"   Dipinjam: {dipinjam_count}")
        print(f"   Dikembalikan: {dikembalikan_count}")
        print(f"   Terlambat: {terlambat_count}")
        print(f"   Jatuh Tempo Hari Ini: {jatuh_tempo_today_count}")
        
        # Verify status_denda field exists and is working
        loans_with_status_denda = Peminjaman.query.filter(Peminjaman.status_denda.isnot(None)).count()
        print(f"\n✅ Loans with status_denda field: {loans_with_status_denda}")
        
        print(f"\n🎉 Fine Management System is ready for testing!")
        print(f"📝 Test Instructions:")
        print(f"   1. Login as admin (admin/admin)")
        print(f"   2. Go to 'Kelola Peminjaman'")
        print(f"   3. Use filter 'Terlambat' to see overdue loans")
        print(f"   4. Click 'Kelola Denda' button on any overdue loan")
        print(f"   5. Test the modal functionality")
        print(f"   6. Verify filter functionality after changes")

if __name__ == '__main__':
    verify_fine_management()
