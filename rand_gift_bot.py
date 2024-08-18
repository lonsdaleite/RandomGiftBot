import asyncio
import re
import time
from datetime import date, datetime, timedelta

from aiogram import types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale

import bot_reply_markup
import common
import notification
import user_state
from db import dml_actions
from db import sql_init
from text_filter import TextFilter

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
                      date="Выбрать дату",
                      cancel="Отмена")


# Handle and remove any state when sending /start and /help
async def handle_start(message: types.Message, state: FSMContext):
    await state.clear()
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
async def validate(message: types.Message = None, state: FSMContext = None, callback: CallbackQuery = None):
    if callback is not None:
        user = common.get_user(tg_id=callback.from_user.id)
    else:
        user = common.get_user(message=message)

    await common.print_log(user, message, state, callback=callback, command_dict=extra_command_dict)

    if user is None:
        await request_user_accept(message, state)
        return None

    current_state = None
    if state is not None:
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

        await state.clear()

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

    msg = "Укажи дату, когда ты в последний раз дарил(а) подарок."
    if user.latest_gift_dt is not None:
        msg += "\nДата, про которую я знаю: " + user.latest_gift_dt
    await state.set_state(user_state.InitialState.waiting_for_set_latest_date)
    calendar = SimpleCalendar(
        locale=await get_user_locale(message.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2000, 1, 1), datetime.today())
    await common.send_message(user.tg_id, msg,
          reply_markup=await calendar.start_calendar())


async def handle_action_set_latest_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    user = await validate(state=state, callback=callback)
    if user is None:
        return

    calendar = SimpleCalendar(
        locale=await get_user_locale(callback.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2000, 1, 1), datetime.today())
    selected, dt = await calendar.process_selection(callback, callback_data)
    if selected:
        dt_str = dt.strftime("%Y-%m-%d")

        user.add_gift(dt_str)
        user.update_user_info(time_to_gift_flg=False)

        msg = "Дата последнего подарка: " + dt_str
        answer_dict = settings_dict
        if not user.check():
            answer_dict = initial_settings_dict
        await state.set_state(user_state.InitialState.waiting_for_settings)
        await callback.message.answer(msg,
            reply_markup=bot_reply_markup.dict_menu(answer_dict, 2)
        )


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
        await state.clear()
        await common.send_message(user.tg_id, "Отлично! Дата последнего подарка установлена",
                                  reply_markup=bot_reply_markup.dict_menu(main_command_dict))


async def handle_days(message: types.Message, state: FSMContext):
    user = await validate(message, state)
    if user is None:
        return
    await state.clear()

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
    await state.clear()
    user = await validate(message, state)
    if user is None:
        return

    response_dict = main_command_dict
    if user.time_to_gift_flg:
        response_dict = extra_command_dict
    await common.send_message(user.tg_id, "Перехожу в главное меню",
                              reply_markup=bot_reply_markup.dict_menu(response_dict))


def register_handlers_main():
    common.dp.message.register(handle_start, TextFilter(['/start', '/help']))
    common.dp.message.register(handle_cancel,
                               TextFilter(['/cancel', 'Отмена', 'Главное меню', 'Время дарить подарки!']))
    common.dp.message.register(handle_action_user_accept, StateFilter(user_state.InitialState.waiting_for_accept))
    common.dp.message.register(handle_set_time_zone,
                               TextFilter(['/time_zone', settings_dict['time_zone']]),
                               StateFilter(user_state.InitialState.waiting_for_settings))
    common.dp.message.register(handle_set_notification_time,
                               TextFilter(['/notification_time', settings_dict['notification_time']]),
                               StateFilter(user_state.InitialState.waiting_for_settings))
    common.dp.message.register(handle_set_days, TextFilter(['/set_days', settings_dict['set_days']]),
                               StateFilter(user_state.InitialState.waiting_for_settings))
    common.dp.message.register(handle_set_latest_date, 
                               TextFilter(['/set_latest_date', settings_dict['set_latest_date']]),
                               StateFilter(user_state.InitialState.waiting_for_settings))
    common.dp.message.register(handle_action_set_time_zone,
                               StateFilter(user_state.InitialState.waiting_for_set_time_zone))
    common.dp.message.register(handle_action_set_notification_time,
                               StateFilter(user_state.InitialState.waiting_for_set_notification_time))
    common.dp.message.register(handle_action_set_days, StateFilter(user_state.InitialState.waiting_for_set_days))
    common.dp.callback_query.register(handle_action_set_latest_date, SimpleCalendarCallback.filter(),
                                      StateFilter(user_state.InitialState.waiting_for_set_latest_date))
    common.dp.message.register(handle_settings, TextFilter(['/settings', extra_command_dict['settings']]))
    common.dp.message.register(handle_days, TextFilter(['/days', extra_command_dict['days']]))
    common.dp.message.register(handle_gift_done, TextFilter(['/gift_done', extra_command_dict['gift_done']]))
    common.dp.message.register(handle_action_gift_done,
                               StateFilter(user_state.InitialState.waiting_for_gift_done))

    common.dp.message.register(handle_welcome)


async def main():
    sql_init.run_scripts()  # DB initialization
    register_handlers_main()
    common.dp.startup.register(notification.run)
    await common.dp.start_polling(common.bot)


if __name__ == '__main__':
    asyncio.run(main())
