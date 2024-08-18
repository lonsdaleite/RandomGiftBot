import traceback
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramAPIError, AiogramError
from aiogram.types import CallbackQuery

import config
import user as us
from db import dml_actions

user_dict = {}

# Bot initialization
bot = Bot(token=config.BOT_TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def print_log(user, message, state, callback: CallbackQuery = None, command_dict=None):
    if callback is not None:
        tg_id = callback.from_user.id
    else:
        tg_id = message.from_user.id
    text = "No text"
    if callback is not None:
        text = callback.data
    elif message.text is not None:
        text = message.text
    elif message.caption is not None:
        text = message.caption

    user_state = ""
    if state is not None:
        user_state = str(await state.get_state())

    if user is None:
        config.logger.info("Unknown user found:\nID: " + str(tg_id))
        if message.from_user.username is not None:
            config.logger.info("UserName: " + message.from_user.username)
        return
    elif command_dict is not None and text[1:] in command_dict or text == '/start':
        config.logger.info("ID: " + str(tg_id) + ", state: " + user_state + ", message: " + text)
    elif command_dict is not None and text in list(command_dict.values()):
        config.logger.info("ID: " + str(tg_id) + ", state: " + user_state + ", message: " + text)
    else:
        config.logger.info("ID: " + str(tg_id) + ", state: " + user_state + ", message: text")

    config.logger.debug("ID: " + str(tg_id) + ", state: " + user_state + ", message: " + text)


async def send_message(tg_id, text, reply_markup=None):
    try:
        if config.DEBUG_TG_ID is not None:
            await bot.send_message(config.DEBUG_TG_ID, "Message to " + str(tg_id) + "\n" + text,
                                   reply_markup=reply_markup)
        else:
            await bot.send_message(tg_id, text, reply_markup=reply_markup)
        pass
    except TelegramAPIError as e:
        if "bot was blocked by the user" in str(e):
            config.logger.warn("Bot blocked for user: " + str(tg_id))
            dml_actions.disable_user(get_user(tg_id=tg_id).user_id)
            user_dict.pop(tg_id)
        else:
            config.logger.debug("Can not send a message to: " + str(tg_id))
            traceback.print_exc()
    except AiogramError:
        config.logger.debug("Can not send a message to: " + str(tg_id))
        traceback.print_exc() 


def get_user(message=None, tg_id=None, user_id=None):
    if message is None and tg_id is None and user_id is None:
        return None

    if message is not None:
        tg_id = message.from_user.id
    
    user = None

    if tg_id is not None and tg_id in user_dict:
        user = user_dict[tg_id]
        if not user.check():
            user.refresh()
    elif tg_id is None:
        for tg_id_tmp, user_tmp in user_dict.items():
            if user_id is not None and user_tmp.user_id == user_id:
                user = user_tmp
                if not user.check():
                    user.refresh()
                    break
    
    if user is None:
        # If tg_id not in dict, create User instance
        user = us.User(user_id, tg_id)
        if user.user_id is None:
            return None
        user_dict[tg_id] = user

    return user
