from aiogram import types

def dict_menu(command_dict, row_width=2):
    markup = types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True)
    markup.add(*list(command_dict.values()))
    return markup

def start():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Старт")
    markup.add(button)
    return markup

def nothing():
    return types.ReplyKeyboardRemove()

def cancel():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Отмена")
    return markup

def user_accept():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Давай начнем!")
    return markup
