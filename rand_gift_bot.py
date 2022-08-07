import re
import time
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
import bot_reply_markup
import common
import notification
import user_state
from db import dml_actions
from db import sql_init

main_command_dict = dict(manual_try='Запустить рандом вручную',
                         days='Сколько дней прошло?',
                         settings='Настройки',
                         help='Помощь с командами')

initial_settings_dict = dict(notification_time='Время для уведомления',
                             set_days='Число дней с последнего подарка')

settings_dict = dict(initial_settings_dict)
settings_dict['cancel'] = 'Главное меню'


# Handle and remove any state when sending /start and /help
async def handle_start(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_welcome(message, state)


async def handle_welcome(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return
    msg = "Привет!\n" \
          + "Я бот, который напоминает дарить цветы и прочие подарки близким людям!\n" \
          + "Я случайным образом выберу день, когда нужно делать подарок, и скажу тебе об этом!\n" \
          + "Вот список команд, которые я понимаю:\n"
    for k, v in main_command_dict.items():
        msg += "/{} : {}\n".format(k, v)
    msg += "А также ты можешь воспользоваться кнопками ниже ⬇️"
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(main_command_dict))


# Main message preparation and validation
# All the handlers call it first
# If user accepted the conversation, returns a User object
# Else returns None
async def validate(message: types.Message, state: FSMContext):
    user = common.get_user(message=message)
    await common.print_log(user, message, state, main_command_dict)

    if user is None:
        await request_user_accept(message, state)
        return None

    current_state = await state.get_state()

    if not user.check() and current_state is None:
        await request_settings(message, state)
        return None

    return user


async def request_user_accept(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    msg = "Привет! Я бот, который напоминает дарить цветы и прочие подарки близким людям! Начнем?"
    await common.send_message(tg_id, msg, reply_markup=bot_reply_markup.user_accept())
    await state.set_state(user_state.InitialState.waiting_for_accept)


async def handle_action_user_accept(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    if message.text == "Давай начнем!":
        user = common.get_user(message=message)
        if user is None:
            dml_actions.add_user(tg_id=tg_id)
            common.get_user(message=message)
        else:
            user.update_user_info(user.user_id, tg_id=tg_id)

        await state.finish()

        user = await validate(message, state)
        if user is not None:
            await handle_welcome(message, state)


async def request_settings(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    await state.set_state(user_state.InitialState.waiting_for_settings)
    msg = "Для начала установи нужные параметры!"
    await common.send_message(tg_id, msg, reply_markup=bot_reply_markup.dict_menu(initial_settings_dict, 1))


async def handle_settings(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    await state.set_state(user_state.InitialState.waiting_for_settings)
    msg = "Установи нужные параметры!"
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(settings_dict, 1))


async def handle_set_notification_time(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    msg = "Выбери время, когда тебе удобно получать уведомления. Введи время в формате ЧЧ:ММ. Например: 13:00"
    if user.notification_time is not None:
        msg += "\nТекущее время для уведомлений: " + user.notification_time
    await state.set_state(user_state.InitialState.waiting_for_set_notification_time)
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_action_set_notification_time(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    try:
        time_str = message.text
        parsed_time = time.strptime(time_str, "%H:%M")
        parsed_time_str = time.strftime("%H:%M", parsed_time)

        user.update_user_info(notification_time=parsed_time_str)

        await state.set_state(user_state.InitialState.waiting_for_settings)
        msg = "Время для уведомлений установлено: " + parsed_time_str
        answer_dict = settings_dict
        if not user.check():
            answer_dict = initial_settings_dict
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(answer_dict, 1))
    except ValueError:
        msg = "Неправильный формат! Введи время в формате ЧЧ:ММ. Например: 13:00"
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_set_days(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    msg = "Выбери интервал в днях, который должно пройти между подарками." \
          "\nЯ буду отправлять уведомления в случайный день в этом промежутке." \
          "\nВведи два числа с любым разделителем: минимальное и максимальное число дней. Например: 14-30"
    if user.min_days_num is not None and user.max_days_num is not None:
        msg += "\nТекущий интервал в днях: " + str(user.min_days_num) + "-" + str(user.max_days_num)
    await state.set_state(user_state.InitialState.waiting_for_set_days)
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_action_set_days(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    try:
        days = re.split(r"[^0-9]+", message.text)
        if len(days) != 2:
            raise ValueError
        min_days_num = int(days[0])
        max_days_num = int(days[1])

        if min_days_num <= 0 or max_days_num <= 0 or min_days_num > max_days_num:
            raise ValueError

        user.update_user_info(min_days_num=min_days_num, max_days_num=max_days_num)

        await state.set_state(user_state.InitialState.waiting_for_settings)
        msg = "Интервал установлен: " + str(user.min_days_num) + "-" + str(user.max_days_num)
        answer_dict = settings_dict
        if not user.check():
            answer_dict = initial_settings_dict
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(answer_dict, 1))
    except ValueError:
        msg = "Неправильный формат! Введи два числа с любым разделителем: минимальное и максимальное число дней. " \
              "Например: 14-30 "
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_manual_try(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return
    await state.finish()
    # TODO


async def handle_days(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return
    await state.finish()

    if user.latest_gift_dt is None:
        msg = "У меня пока нет информации о последнем подарке"
    else:
        msg = "С последнего подарка прошло " + str(user.latest_gift_dt) + " дней!"
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(main_command_dict))


async def handle_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_welcome(message, state)


def register_handlers_main():
    common.dp.register_message_handler(handle_start, commands=['start', 'help'], state='*')
    common.dp.register_message_handler(handle_cancel, text=['/cancel', 'Отмена', 'Главное меню'], state='*')
    common.dp.register_message_handler(handle_action_user_accept, state=user_state.InitialState.waiting_for_accept)
    common.dp.register_message_handler(handle_set_notification_time,
                                       text=['/notification_time', settings_dict['notification_time']],
                                       state=[user_state.InitialState.waiting_for_settings])
    common.dp.register_message_handler(handle_set_days, text=['/set_days', settings_dict['set_days']],
                                       state=[user_state.InitialState.waiting_for_settings])
    common.dp.register_message_handler(handle_action_set_notification_time,
                                       state=[user_state.InitialState.waiting_for_set_notification_time])
    common.dp.register_message_handler(handle_action_set_days, state=[user_state.InitialState.waiting_for_set_days])
    common.dp.register_message_handler(handle_settings, text=['/settings', main_command_dict['settings']])
    common.dp.register_message_handler(handle_days, text=['/days', main_command_dict['days']])
    common.dp.register_message_handler(handle_manual_try, text=['/manual_try', main_command_dict['manual_try']])

    common.dp.register_message_handler(handle_welcome)


# DB initialization
sql_init.run_scripts()

register_handlers_main()

executor.start_polling(common.dp, skip_updates=False, on_startup=notification.run)
