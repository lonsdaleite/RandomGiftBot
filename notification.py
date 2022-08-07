import asyncio
import aioschedule
import time
import common
import config
import randomize
from db import select_actions
from db import dml_actions


async def notify_user(user):
    await common.send_message(user.tg_id, "Время дарить подарки!")
    dml_actions.add_notification_log(user.user_id, user.notification_time)
    config.logger.info("Notification sent to " + str(user.tg_id))


async def notify():
    tg_id_list = select_actions.get_tg_id_by_time(time.strftime("%H:%M", time.localtime()))
    for tg_id in tg_id_list:
        user = common.get_user(tg_id=tg_id)
        if randomize.send_or_not(user):
            notify_user(user)


async def scheduler(bot):
    aioschedule.every().minute.do(notify)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def run(dp):
    asyncio.create_task(scheduler(dp.bot))
