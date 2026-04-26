"""
MAGER - Auth Logic
Login & Register dengan MySQL, password di-hash pakai bcrypt.
"""

import bcrypt
import mysql.connector
from mysql.connector import Error as MySQLError

from database.connection import connection_database


# ─────────────────────────────────────────────────────────────────────────────
# Helper koneksi
# ─────────────────────────────────────────────────────────────────────────────
def _conn():
    return connection_database()


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────
def login_user(username: str, password: str) -> dict:
    """
    Return:
        {"success": True,  "user": {"id_user": ..., "username": ...}}
        {"success": False, "message": "..."}
    """
    try:
        conn   = _conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = %s LIMIT 1",
            (username,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return {"success": False, "message": "Username tidak ditemukan."}

        # Verifikasi password
        stored_hash = row["password"].encode() if isinstance(row["password"], str) else row["password"]
        if not bcrypt.checkpw(password.encode(), stored_hash):
            return {"success": False, "message": "Password salah."}

        return {
            "success": True,
            "user": {
                "id_user":  row["id_user"],
                "username": row["username"],
            }
        }

    except MySQLError as e:
        print(f"[auth_logic] Login DB error: {e}")
        return {"success": False, "message": "Terjadi kesalahan koneksi database."}


# ─────────────────────────────────────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────────────────────────────────────
def register_user(username: str, password: str) -> dict:
    """
    Return:
        {"success": True}
        {"success": False, "message": "..."}
    """
    try:
        conn   = _conn()
        cursor = conn.cursor()

        # Cek username sudah ada
        cursor.execute(
            "SELECT id_user FROM users WHERE username = %s LIMIT 1",
            (username,)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "Username sudah digunakan."}

        # Hash password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed.decode())
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True}

    except MySQLError as e:
        print(f"[auth_logic] Register DB error: {e}")
        return {"success": False, "message": "Terjadi kesalahan koneksi database."}