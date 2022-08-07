import config
from db import sql_connect


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


def get_latest_notification_log(user_id):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT processed_dttm
        FROM notification_log
        WHERE user_id = ? and is_active_flg = '1'
        """, (user_id, ))
    row = cursor.fetchone()

    if row is None:
        config.logger.warn("Notification log for user " + str(user_id) + " not found")
        return None
    
    cursor.close()
    conn.close()
    return row


def get_latest_random_log(user_id):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT processed_dttm
        FROM random_log 
        WHERE user_id = ? and is_active_flg = '1'
        """, (user_id, ))
    row = cursor.fetchone()

    if row is None:
        config.logger.warn("Random log for user " + str(user_id) + " not found")
        return None
    
    cursor.close()
    conn.close()
    return row


def get_tg_id_by_time(notification_time):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tg_id 
        FROM user
        WHERE 1=1
            and deleted_flg = '0'
            and notification_time = ?
        """, (notification_time, ))
    result = cursor.fetchall()
    tg_id_list = [x["tg_id"] for x in result]

    cursor.close()
    conn.close()
    return tg_id_list
