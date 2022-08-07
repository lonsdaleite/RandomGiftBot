from db import sql_connect
import config


def run_scripts(recreate=False):
    conn = sql_connect.create_connection()
    cursor = conn.cursor()

    if recreate:
        with open(config.SQLITE3_SCRIPT_DIR + '/drop_all.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)

    for file in ["user.sql", "gift.sql", "notification_log.sql", "random_log.sql"]:
        with open(config.SQLITE3_SCRIPT_DIR + '/' + file, 'r') as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)

    conn.commit()
    cursor.close()
    conn.close()
