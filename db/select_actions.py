import config
from db import sql_connect


def get_user_info(user_id, tg_id):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    if user_id is None and tg_id is None:
        config.logger.error("Can't get user info without arguments")
        return

    cursor.execute("""
        SELECT user_id, tg_id, time_zone, notification_time, min_days_num, max_days_num, time_to_gift_flg
        FROM user 
        WHERE (user_id = ? or tg_id = ?) and deleted_flg = '0'
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
        SELECT gift_dt
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


def get_user_id_by_time(utc_notification_time):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id 
        FROM user
        WHERE 1=1
            and deleted_flg = '0'
            and notification_time = substring(time(?, 
                case
                    when time_zone >= 0 then '+' || cast(time_zone as varchar)
                    else cast(time_zone as varchar)
                end || ' hours'), 1, 5)
        """, (utc_notification_time, ))
    result = cursor.fetchall()
    user_id_list = [x["user_id"] for x in result]

    cursor.close()
    conn.close()
    return user_id_list
