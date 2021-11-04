from db import sql_connect
from db import select_actions
from datetime import datetime
import config


def add_user_info(user_id, tg_id=None, notification_time=None, min_days_num=None, max_days_num=None):
    if user_id is None:
        config.logger.error("Can not add a user info without user_id")
        return

    if tg_id is None or notification_time is None or min_days_num is None or max_days_num is None:
        config.logger.error("Can't update user_id: " + str(user_id) + " info. No arguments passed.")
        return

    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT count(*) 
        FROM user 
        WHERE user_id = ?
        """, (user_id, ))

    if cursor.fetchone()[0] == 0:
        config.logger.error("user_id " + str(user_id) + " does not exist")
        cursor.close()
        conn.close()
        return

    if tg_id is not None:
        cursor.execute("""
            UPDATE user
            SET tg_id = ?
            WHERE user_id = ?
            """, (tg_id, user_id))

    if notification_time is not None:
        cursor.execute("""
            UPDATE user
            SET notification_time = ?
            WHERE user_id = ?
            """, (notification_time, user_id))

    if min_days_num is not None:
        cursor.execute("""
            UPDATE user
            SET min_days_num = ?
            WHERE user_id = ?
            """, (min_days_num, user_id))

    if max_days_num is not None:
        cursor.execute("""
            UPDATE user
            SET max_days_num = ?
            WHERE user_id = ?
            """, (max_days_num, user_id))

    config.logger.info("user_id: " + str(user_id) + " tg_id: " + str(tg_id) + " info updated")

    conn.commit()
    cursor.close()
    conn.close()


def add_user(tg_id=None):
    if tg_id is None:
        config.logger.error("Can not add a user without telegram id")
        return

    conn = sql_connect.create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT count(*) 
        FROM user 
        WHERE tg_id = ?
        """, (tg_id, ))

    if cursor.fetchone()[0] > 0:
        config.logger.error("tg_id: " + str(tg_id) + " already exists")
        cursor.close()
        conn.close()
        return

    cursor.execute("""
        SELECT coalesce(max(user_id), 0) + 1 
        FROM user 
        """)
    user_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO user (user_id, tg_id, processed_dttm) 
        VALUES (?, ?, ?)
        """, (user_id, tg_id, datetime.now()))

    config.logger.info("user_id: " + str(user_id) + " tg_id: " + str(tg_id) + " added")

    conn.commit()
    cursor.close()
    conn.close()

    return user_id


def add_gift_dt(user_id, gift_dt):
    if user_id is None:
        config.logger.error("Can not add a gift info without user_id")
        return

    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gift
        SET is_active_flg = '0'
        WHERE user_id = ?
        """, (user_id, ))

    cursor.execute("""
    INSERT INTO gift (user_id, gift_dt, is_active_flg, processed_dttm) 
    VALUES (?, ?, ?, ?)
    """, (user_id, gift_dt, '1', datetime.now()))


    config.logger.info("user_id: " + str(user_id) + " gift_dt: " + str(gift_dt) + " added")

    conn.commit()
    cursor.close()
    conn.close()
