import os
import mysql.connector
from mysql.connector import Error

DB_HOST = os.getenv("MYSQLHOST", os.getenv("DB_HOST", "localhost"))
DB_PORT = int(os.getenv("MYSQLPORT", os.getenv("DB_PORT", "3306")))
DB_USER = os.getenv("MYSQLUSER", os.getenv("DB_USER", "root"))
DB_PASSWORD = os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD", ""))
DB_NAME = os.getenv("MYSQLDATABASE", os.getenv("DB_NAME", "bank_management"))


db = None


def connect_database():
    global db
    try:
        if db is not None and db.is_connected():
            return True
        db = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=10,
        )
        return db.is_connected()
    except Error as e:
        print("Database connection failed:", e)
        db = None
        return False


def is_database_connected():
    global db
    try:
        return db is not None and db.is_connected()
    except Error:
        return False


def reconnect_database():
    return connect_database()


def get_database():
    if is_database_connected() or connect_database():
        return db
    return None


connect_database()
