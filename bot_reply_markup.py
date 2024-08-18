from aiogram import types


def dict_menu(command_dict, row_width=2):
    buttons = [types.KeyboardButton(text=command) for command in command_dict.values()]
    # Split buttons into rows of row_width
    keyboard = [buttons[i:i + row_width] for i in range(0, len(buttons), row_width)]
    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    return markup


def simple_button(text):
    return types.ReplyKeyboardMarkup(keyboard = [[types.KeyboardButton(text=text)]], resize_keyboard=True)

def start():
    return simple_button("Старт")


def nothing():
    return types.ReplyKeyboardRemove()


def cancel():
    return simple_button("Отмена")


def user_accept():
    return simple_button("Давай начнем!")


def time_to_gift():
    return simple_button("Время дарить подарки!")
