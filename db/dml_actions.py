from datetime import datetime
import config
from db import sql_connect


def update_user_info(user_id, tg_id=None, notification_time=None, min_days_num=None, max_days_num=None,
                     time_to_gift_flg=None):
    if user_id is None:
        config.logger.error("Can not add a user info without user_id")
        return

    if tg_id is None and notification_time is None and min_days_num is None and max_days_num is None \
            and time_to_gift_flg is None:
        config.logger.error("Can't update user_id: " + str(user_id) + " info. No arguments passed.")
        return

    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT count(*) 
        FROM user 
        WHERE user_id = ? and deleted_flg = '0'
        """, (user_id,))

    if cursor.fetchone()[0] == 0:
        config.logger.error("user_id " + str(user_id) + " does not exist")
        cursor.close()
        conn.close()
        return

    if tg_id is not None:
        cursor.execute("""
            UPDATE user
            SET tg_id = ?
            WHERE user_id = ? and deleted_flg = '0'
            """, (tg_id, user_id))

    if notification_time is not None:
        cursor.execute("""
            UPDATE user
            SET notification_time = ?
            WHERE user_id = ? and deleted_flg = '0'
            """, (notification_time, user_id))

    if min_days_num is not None:
        cursor.execute("""
            UPDATE user
            SET min_days_num = ?
            WHERE user_id = ? and deleted_flg = '0'
            """, (min_days_num, user_id))

    if max_days_num is not None:
        cursor.execute("""
            UPDATE user
            SET max_days_num = ?
            WHERE user_id = ? and deleted_flg = '0'
            """, (max_days_num, user_id))

    if time_to_gift_flg is not None:
        cursor.execute("""
            UPDATE user
            SET time_to_gift_flg = ?
            WHERE user_id = ? and deleted_flg = '0'
            """, (time_to_gift_flg, user_id))

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
        SELECT user_id, deleted_flg
        FROM user 
        WHERE tg_id = ?
        """, (tg_id,))

    row = cursor.fetchone()

    if row is None:
        cursor.execute("""
            SELECT coalesce(max(user_id), 0) + 1 
            FROM user 
            """)
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO user (user_id, tg_id, time_to_gift_flg, deleted_flg, processed_dttm) 
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, tg_id, '0', '0', datetime.now()))

        config.logger.info("user_id: " + str(user_id) + " tg_id: " + str(tg_id) + " added")
    elif row['deleted_flg'] == '0':
        config.logger.error("tg_id: " + str(tg_id) + " already exists")
        cursor.close()
        conn.close()
        return None
    elif row['deleted_flg'] == '1':
        cursor.execute("""
            UPDATE user
            SET deleted_flg = '0'
            WHERE tg_id = ?
            """, (tg_id,))

        user_id = row['user_id']
        config.logger.info("tg_id: " + str(tg_id) + " enabled")

    conn.commit()
    cursor.close()
    conn.close()

    return user_id


def add_gift(user_id, gift_dt):
    if user_id is None:
        config.logger.error("Can not add a gift info without user_id")
        return

    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gift
        SET is_active_flg = '0'
        WHERE user_id = ?
        """, (user_id,))

    cursor.execute("""
    INSERT INTO gift (user_id, gift_dt, is_active_flg, processed_dttm) 
    VALUES (?, ?, ?, ?)
    """, (user_id, gift_dt, '1', datetime.now()))

    config.logger.info("user_id: " + str(user_id) + " gift_dt: " + str(gift_dt) + " added")

    conn.commit()
    cursor.close()
    conn.close()


def add_notification_log(user_id, notification_time, sent_flg):
    if user_id is None:
        config.logger.error("Can not log info without user_id")
        return

    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notification_log
        SET is_active_flg = '0'
        WHERE user_id = ?
        """, (user_id,))

    cursor.execute("""
    INSERT INTO notification_log (user_id, notification_time, sent_flg, is_active_flg, processed_dttm) 
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, notification_time, sent_flg, '1', datetime.now()))

    config.logger.info("user_id: " + str(user_id) + " notification log added")

    conn.commit()
    cursor.close()
    conn.close()


def add_random_log(user_id, since_latest_gift_days_cnt, random_days_cnt):
    if user_id is None:
        config.logger.error("Can not log info without user_id")
        return

    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE random_log
        SET is_active_flg = '0'
        WHERE user_id = ?
        """, (user_id,))

    cursor.execute("""
    INSERT INTO random_log (user_id, since_latest_gift_days_cnt, random_days_cnt, is_active_flg, processed_dttm) 
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, since_latest_gift_days_cnt, random_days_cnt, '1', datetime.now()))

    config.logger.info("user_id: " + str(user_id) + " random log added")

    conn.commit()
    cursor.close()
    conn.close()
