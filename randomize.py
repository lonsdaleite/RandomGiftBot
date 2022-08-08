from datetime import date, datetime
from random import randrange
import config
from db import dml_actions


def send_or_not(user):
    today = date.today()
    config.logger.debug("user_id: " + str(user.user_id) + ", today: " + today.strftime("%Y-%m-%d"))

    since_last_day = (today - datetime.strptime(user.latest_gift_dt, "%Y-%m-%d").date()).days
    config.logger.debug("user_id: " + str(user.user_id) + ", since_last_day: " + str(since_last_day))

    if user.time_to_gift_flg:
        dml_actions.add_random_log(user.user_id, since_last_day, None)
        return True
    elif since_last_day >= user.max_days_num:
        dml_actions.add_random_log(user.user_id, since_last_day, None)
        user.update_user_info(time_to_gift_flg=True)
        return True
    elif since_last_day < user.min_days_num:
        dml_actions.add_random_log(user.user_id, since_last_day, None)
        return False

    rand_days_cnt = randrange(since_last_day, user.max_days_num + 1)
    dml_actions.add_random_log(user.user_id, since_last_day, rand_days_cnt)
    config.logger.debug("user_id: " + str(user.user_id) + ", rand_days_cnt: " + str(rand_days_cnt))
    if rand_days_cnt == since_last_day:
        user.update_user_info(time_to_gift_flg=True)
        return True
    return False
