import asyncio
import aioschedule
import time
import common
import config
from db import select_actions

async def notify(bot):
    tg_id_list = select_actions.get_tg_id_by_time(time.strftime("%H:%M", time.localtime()))
    for tg_id in tg_id_list:
        user = common.get_user(tg_id=tg_id)
        # await common.send_message(bot, tg_id, "Ежедневное напоминание! Твой вишлист всё ещё пуст! Добавь желание, а то бедному Санте не из чего выбирать 🙁")
        config.logger.info("Notification sent to " + str(tg_id))

async def scheduler(bot):
    aioschedule.every().minute.do(notify, bot=bot)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def run(dp):
    asyncio.create_task(scheduler(dp.bot))
