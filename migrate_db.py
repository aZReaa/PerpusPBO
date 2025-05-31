#!/usr/bin/env python3
"""
Database migration script to add profile_photo column to user table
"""

import sqlite3
import os

def migrate_database():
    db_path = 'instance/perpustakaan.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database with updated schema.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if profile_photo column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'profile_photo' not in columns:
            print("Adding profile_photo column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN profile_photo VARCHAR(200)")
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("✅ profile_photo column already exists.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
