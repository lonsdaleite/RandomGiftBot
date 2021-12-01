from db import sql_connect
from datetime import datetime
import config

def get_user_info(user_id, tg_id):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    if user_id is None and tg_id is None:
        config.logger.error("Can't get user info without arguments")
        return

    cursor.execute("""
        SELECT user_id, tg_id, notification_time, min_days_num, max_days_num
        FROM user 
        WHERE user_id = ? or tg_id = ?
        """, (user_id, tg_id))
    row = cursor.fetchone()

    if row is None:
        config.logger.error("user_id: " + str(user_id) + " tg_id: " + str(tg_id) + " does not exist")

    cursor.close()
    conn.close()
    return row


def get_latest_gift(user_id):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT gift_dt, done_flg
        FROM gift 
        WHERE user_id = ? and is_active_flg = '1'
        """, (user_id, ))
    row = cursor.fetchone()

    if row is None:
        config.logger.warn("Gift dt for user " + str(user_id) + " not found")
        return None
    
    cursor.close()
    conn.close()
    return row
