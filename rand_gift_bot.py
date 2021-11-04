from random import randrange
from datetime import datetime, date, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import traceback
import logging
import config
import user
from db import sql_init
from db import dml_actions
import bot_reply_markup
import common
import user_state


main_command_dict = dict(   manual_try='Запустить рандом вручную',
                            days='Сколько дней прошло?',
                            settings='Настройки',
                            help='Помощь с командами')


settings_dict = dict(   notification_time='Время для уведомления',
                        min_days='Минимальное число дней с последнего подарка',
                        max_days='Максимальное число дней с последнего подарка',
                        cancel='Отмена')


# Handle and remove any state when sending /start and /help
async def handle_start(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_welcome(message, state)


async def handle_welcome(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return
    welcome_message = "Привет!\nЯ бот, который напоминает дарить цветы и прочие подарки близким людям!\nВот список команд, которые я понимаю:\n"
    for k, v in main_command_dict.items():
        welcome_message += "/{} : {}\n".format(k, v)
    welcome_message += "А также ты можешь воспользоваться кнопками ниже ⬇️"
    await common.send_message(user.tg_id, welcome_message, reply_markup=bot_reply_markup.dict_menu(main_command_dict))


# Main message preparation and validation
# All the handlers call it first
# If the game already started, returns a User object
# Else returns None
async def validate(message: types.Message, state: FSMContext):
    user = common.get_user(message=message)
    await common.print_log(user, message, state, main_command_dict)

    if user is None:
        await request_user_accept(message, state)
        return None

    if not user.check():
        await request_settings(message, state)
        return None

    return user


async def request_user_accept(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    await common.send_message(tg_id, 
        "Привет! Я бот, который напоминает дарить цветы и прочие подарки близким людям! Начнем?", 
        reply_markup=bot_reply_markup.user_accept())
    await state.set_state(user_state.InitialState.waiting_for_accept)


async def handle_action_user_accept(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    if message.text == "Давай начнем!":
        user = common.get_user(message=message)
        if user is None:
            dml_actions.add_user(tg_id=tg_id)
            user = common.get_user(message=message)
        else:
            dml_actions.add_user_info(user.user_id, tg_id=tg_id)
        
        await state.finish()
        
        user = await validate(message, state)
        if user is not None:
            handle_welcome(message, state)


async def request_settings(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    await state.set_state(user_state.InitialState.waiting_for_settings)
    settings_message = "Для начала установи нужные параметры!"
    await common.send_message(tg_id, settings_message, reply_markup=bot_reply_markup.dict_menu(settings_dict, 1))


async def handle_manual_try(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return


async def handle_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_welcome(message, state)


def register_handlers_main(dp: Dispatcher):
    common.dp.register_message_handler(handle_start, commands=['start', 'help'], state='*')
    common.dp.register_message_handler(handle_action_user_accept, state=user_state.InitialState.waiting_for_accept)
    common.dp.register_message_handler(handle_cancel, text=['/cancel', 'Отмена'], state=[user_state.InitialState.waiting_for_settings])
    
    common.dp.register_message_handler(handle_welcome)


# DB initialization
sql_init.run_scripts()

register_handlers_main(common.dp)

executor.start_polling(common.dp, skip_updates=False)
