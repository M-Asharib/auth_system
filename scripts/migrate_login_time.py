import sqlite3
import os

db_path = "e:/SMIT/auth_system/sql_app.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT last_login_at FROM users LIMIT 1;")
        print("Column last_login_at exists.")
    except sqlite3.OperationalError:
        print("Column last_login_at missing, adding...")
        cursor.execute("ALTER TABLE users ADD COLUMN last_login_at DATETIME;")
        conn.commit()
        print("Column last_login_at added.")
    conn.close()
else:
    print("Database not found.")
