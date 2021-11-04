import configparser
import sys
import logging

#logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
log_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
log_handler.setFormatter(log_format)
logger.addHandler(log_handler)

config = configparser.ConfigParser()
config.read("config.ini")
config.read("user_config.ini")

DEBUG = False
debug_str = config.get("debug", "debug", fallback="False")
if debug_str.lower() in ['true', '1', 't', 'y', 'yes']:
    DEBUG = True

if DEBUG:
    logger.setLevel(logging.DEBUG)

DEBUG_TG_ID = int(config.get("debug", "debug_tg_id", fallback="-1"))
if DEBUG_TG_ID == -1:
    DEBUG_TG_ID = None

SQLITE3_DB = config.get("sqlite3", "db_file", fallback=None)
SQLITE3_SCRIPT_DIR = config.get("sqlite3", "sql_scripts", fallback=None)

BOT_TG_TOKEN = config.get("bot", "bot_tg_token", fallback=None)

if SQLITE3_DB is None or SQLITE3_DB == "":
    sys.exit("ERROR: [sqlite3]/db_file parameter must be set in config.ini or user_config.ini")

if SQLITE3_SCRIPT_DIR is None or SQLITE3_SCRIPT_DIR == "":
    sys.exit("ERROR: [sqlite3]/sql_scripts parameter must be set in config.ini or user_config.ini")

if BOT_TG_TOKEN is None or BOT_TG_TOKEN == "":
    sys.exit("ERROR: [bot]/bot_tg_token parameter must be set in config.ini or user_config.ini")
