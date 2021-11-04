import config
import sqlite3
from datetime import datetime

def create_connection():
    conn = sqlite3.connect(config.SQLITE3_DB)
    conn.row_factory = sqlite3.Row
    return conn
