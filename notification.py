import asyncio
import aioschedule
import time

import bot_reply_markup
import common
import config
import randomize
from db import select_actions
from db import dml_actions


async def notify_user(user):
    await common.send_message(user.tg_id, "Время дарить подарки!", reply_markup=bot_reply_markup.time_to_gift())
    dml_actions.add_notification_log(user.user_id, user.time_zone, user.notification_time, "1")
    config.logger.info("Notification sent to " + str(user.tg_id))


async def notify():
    user_id_list = select_actions.get_user_id_by_time(time.strftime("%H:%M", time.gmtime()))
    for user_id in user_id_list:
        user = common.get_user(user_id=user_id)
        if user.check() and randomize.send_or_not(user):
            await notify_user(user)
        else:
            dml_actions.add_notification_log(user.user_id, user.time_zone, user.notification_time, "0")


async def scheduler():
    aioschedule.every().minute.do(notify)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def run():
    asyncio.create_task(scheduler())
