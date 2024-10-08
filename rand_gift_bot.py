from datetime import date, datetime, timedelta
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

main_command_dict = dict(days='Сколько дней прошло?',
                         settings='Настройки',
                         help='Помощь с командами')

extra_command_dict = dict(gift_done='Подарок подарен')
extra_command_dict.update(main_command_dict)

initial_settings_dict = dict(time_zone='Часовой пояс',
                             notification_time='Время для уведомления',
                             set_days='Диапазон дней',
                             set_latest_date='Дата последнего подарка')

settings_dict = dict(initial_settings_dict)
settings_dict['cancel'] = 'Главное меню'

gift_done_dict = dict(today="Сегодня",
                      yesterday="Вчера",
                      date="Ввести дату",
                      cancel="Отмена")


# Handle and remove any state when sending /start and /help
async def handle_start(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_welcome(message, state)


async def handle_welcome(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    response_dict = main_command_dict
    if user.time_to_gift_flg:
        response_dict = extra_command_dict

    msg = "Привет!\n" \
          + "Я бот, который напоминает дарить цветы и прочие подарки близким людям!\n" \
          + "Я случайным образом выберу день, когда нужно делать подарок, и скажу тебе об этом!\n" \
          + "Вот список команд, которые я понимаю:\n"
    for k, v in response_dict.items():
        msg += "/{} : {}\n".format(k, v)
    msg += "А также ты можешь воспользоваться кнопками ниже ⬇️"

    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(response_dict))


# Main message preparation and validation
# All the handlers call it first
# If user accepted the conversation, returns a User object
# Else returns None
async def validate(message: types.Message, state: FSMContext):
    user = common.get_user(message=message)
    await common.print_log(user, message, state, extra_command_dict)

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
    await common.send_message(tg_id, msg, reply_markup=bot_reply_markup.dict_menu(initial_settings_dict, 2))


async def handle_settings(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    await state.set_state(user_state.InitialState.waiting_for_settings)
    msg = "Установи нужные параметры!"
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(settings_dict, 2))


async def handle_set_time_zone(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    msg = "Установи свой часовой пояс. Введи значение в формате +Ч или -Ч. Например, +3 для Москвы."
    if user.time_zone is not None:
        if user.time_zone >= 0:
            time_zone_str = "+" + str(user.time_zone)
        else:
            time_zone_str = str(user.time_zone)
        msg += "\nТекущий часовой пояс: UTC" + time_zone_str
    await state.set_state(user_state.InitialState.waiting_for_set_time_zone)
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_action_set_time_zone(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    try:
        time_zone_str = message.text
        time_zone = int(time_zone_str)

        if time_zone < -12 or time_zone > 14:
            raise ValueError

        user.update_user_info(time_zone=time_zone)

        if user.time_zone >= 0:
            time_zone_str = "+" + str(user.time_zone)
        else:
            time_zone_str = str(user.time_zone)

        await state.set_state(user_state.InitialState.waiting_for_settings)
        msg = "Часовой пояс установлен: UTC" + time_zone_str
        answer_dict = settings_dict
        if not user.check():
            answer_dict = initial_settings_dict
        await state.set_state(user_state.InitialState.waiting_for_settings)
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(answer_dict, 2))
    except ValueError:
        msg = "Неправильный формат! Введи значение в формате +Ч или -Ч. Например, +3 для Москвы."
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_set_notification_time(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    msg = "Выбери время, когда тебе удобно получать уведомления. Введи время в формате ЧЧ:ММ. Например: " \
          "13:00"
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
        await state.set_state(user_state.InitialState.waiting_for_settings)
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(answer_dict, 2))
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
        await state.set_state(user_state.InitialState.waiting_for_settings)
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(answer_dict, 2))
    except ValueError:
        msg = "Неправильный формат! Введи два числа с любым разделителем: минимальное и максимальное число дней. " \
              "Например: 14-30 "
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_set_latest_date(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    msg = "Укажи дату, когда ты в последний раз дарил(а) подарок. Формат даты YYYY-MM-DD. Например: 2022-04-15."
    if user.latest_gift_dt is not None:
        msg += "\nДата, про которую я знаю: " + user.latest_gift_dt
    await state.set_state(user_state.InitialState.waiting_for_set_latest_date)
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_action_set_latest_date(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    try:
        dt_str = message.text
        parsed_dt = datetime.strptime(dt_str, "%Y-%m-%d")

        user.add_gift(dt_str)
        user.update_user_info(time_to_gift_flg=False)

        await state.set_state(user_state.InitialState.waiting_for_settings)
        msg = "Дата последнего подарка: " + dt_str
        answer_dict = settings_dict
        if not user.check():
            answer_dict = initial_settings_dict
        await state.set_state(user_state.InitialState.waiting_for_settings)
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(answer_dict, 2))
    except ValueError:
        msg = "Неправильный формат! Формат даты YYYY-MM-DD. Например: 2022-04-15."
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.cancel())


async def handle_gift_done(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    if user.time_to_gift_flg:
        msg = "Когда ты подарил(а) подарок?"
        await state.set_state(user_state.InitialState.waiting_for_gift_done)
        await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(gift_done_dict, 2))


async def handle_action_gift_done(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return

    if message.text == gift_done_dict["date"]:
        await handle_set_latest_date(message, state)
    else:
        if message.text == gift_done_dict["today"]:
            user.add_gift(date.today().strftime("%Y-%m-%d"))
        elif message.text == gift_done_dict["yesterday"]:
            user.add_gift((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"))
        else:
            msg = "Неверная команда, попробуй еще раз"
            await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(gift_done_dict, 2))
            return

        user.update_user_info(time_to_gift_flg=False)
        await state.finish()
        await common.send_message(user.tg_id, "Отлично! Дата последнего подарка установлена",
                                  reply_markup=bot_reply_markup.dict_menu(main_command_dict))


async def handle_days(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return
    await state.finish()

    if user.latest_gift_dt is None:
        msg = "У меня пока нет информации о последнем подарке"
    else:
        msg = "С последнего подарка прошло " + \
              str((date.today() - datetime.strptime(user.latest_gift_dt, "%Y-%m-%d").date()).days) + " дней!"

    response_dict = main_command_dict
    if user.time_to_gift_flg:
        response_dict = extra_command_dict
    await common.send_message(user.tg_id, msg, reply_markup=bot_reply_markup.dict_menu(response_dict))


async def handle_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    user = await validate(message, state)
    if user is None:
        return

    response_dict = main_command_dict
    if user.time_to_gift_flg:
        response_dict = extra_command_dict
    await common.send_message(user.tg_id, "Перехожу в главное меню",
                              reply_markup=bot_reply_markup.dict_menu(response_dict))


def register_handlers_main():
    common.dp.register_message_handler(handle_start, commands=['start', 'help'], state='*')
    common.dp.register_message_handler(handle_cancel,
                                       text=['/cancel', 'Отмена', 'Главное меню', 'Время дарить подарки!'], state='*')
    common.dp.register_message_handler(handle_action_user_accept, state=user_state.InitialState.waiting_for_accept)
    common.dp.register_message_handler(handle_set_time_zone,
                                       text=['/time_zone', settings_dict['time_zone']],
                                       state=[user_state.InitialState.waiting_for_settings])
    common.dp.register_message_handler(handle_set_notification_time,
                                       text=['/notification_time', settings_dict['notification_time']],
                                       state=[user_state.InitialState.waiting_for_settings])
    common.dp.register_message_handler(handle_set_days, text=['/set_days', settings_dict['set_days']],
                                       state=[user_state.InitialState.waiting_for_settings])
    common.dp.register_message_handler(handle_set_latest_date, text=['/set_latest_date',
                                       settings_dict['set_latest_date']],
                                       state=[user_state.InitialState.waiting_for_settings])
    common.dp.register_message_handler(handle_action_set_time_zone,
                                       state=[user_state.InitialState.waiting_for_set_time_zone])
    common.dp.register_message_handler(handle_action_set_notification_time,
                                       state=[user_state.InitialState.waiting_for_set_notification_time])
    common.dp.register_message_handler(handle_action_set_days, state=[user_state.InitialState.waiting_for_set_days])
    common.dp.register_message_handler(handle_action_set_latest_date,
                                       state=[user_state.InitialState.waiting_for_set_latest_date])
    common.dp.register_message_handler(handle_settings, text=['/settings', extra_command_dict['settings']])
    common.dp.register_message_handler(handle_days, text=['/days', extra_command_dict['days']])
    common.dp.register_message_handler(handle_gift_done, text=['/gift_done', extra_command_dict['gift_done']])
    common.dp.register_message_handler(handle_action_gift_done,
                                       state=[user_state.InitialState.waiting_for_gift_done])

    common.dp.register_message_handler(handle_welcome)


# DB initialization
sql_init.run_scripts()

register_handlers_main()

executor.start_polling(common.dp, skip_updates=False, on_startup=notification.run)
