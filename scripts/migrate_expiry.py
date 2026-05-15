import sqlite3
import os

db_path = "e:/SMIT/auth_system/sql_app.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT access_token_expires_minutes FROM users LIMIT 1;")
        print("Column exists.")
    except sqlite3.OperationalError:
        print("Column missing, adding...")
        cursor.execute("ALTER TABLE users ADD COLUMN access_token_expires_minutes INTEGER;")
        conn.commit()
        print("Column added.")
    conn.close()
