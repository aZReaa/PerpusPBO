#!/usr/bin/env python3
"""
Migration script to add status_denda column to peminjaman table
"""

import sqlite3
import os

def migrate_database():
    db_path = 'instance/perpustakaan.db'
    
    if not os.path.exists(db_path):
        print('Database file not found')
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(peminjaman)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status_denda' in columns:
            print('Column status_denda already exists')
        else:
            # Add the status_denda column with default value
            cursor.execute('ALTER TABLE peminjaman ADD COLUMN status_denda VARCHAR(20) DEFAULT "Belum Lunas"')
            conn.commit()
            print('Successfully added status_denda column to peminjaman table')
            
            # Update existing records to have default value
            cursor.execute('UPDATE peminjaman SET status_denda = "Belum Lunas" WHERE status_denda IS NULL')
            conn.commit()
            print('Updated existing records with default status_denda value')
            
    except sqlite3.Error as e:
        print(f'Database error: {e}')
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
