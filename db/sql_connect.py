import sqlite3
import config


def create_connection():
    conn = sqlite3.connect(config.SQLITE3_DB)
    conn.row_factory = sqlite3.Row
    return conn
