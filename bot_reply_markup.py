from aiogram import types

def dict_menu(command_dict, row_width=2):
    markup = types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True)
    markup.add(*list(command_dict.values()))
    return markup

def delete_wish(user):
    markup = types.ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
    wish_num_list=user.get_wishlist_num()
    markup.add("Отмена")
    markup.add(*wish_num_list)
    return markup

def send_phone_num():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    markup.add(button)
    return markup

def start():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text="Старт")
    markup.add(button)
    return markup

def sex():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Мужской", "Женский")
    return markup

def nothing():
    return types.ReplyKeyboardRemove()

def cancel():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Отмена")
    return markup

def join_or_create_game(command_dict):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(*list(command_dict.values()))
    return markup 

def user_accept():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Давай начнем!")
    return markup

def leader_choose_group(groups):
    markup = types.ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
    markup.add("Отмена")
    markup.add("Создать новую группу")
    group_list = []
    for group in groups:
        group_list.append(str(group))
    markup.add(*group_list)
    return markup

def leader_choose_user(users):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Отмена")
    user_text_list = []
    for user in users:
        text = user.phone_number
        if user.full_name is not None:
                text += " " + user.full_name
        user_text_list.append(text)
    markup.add(*user_text_list)
    return markup
