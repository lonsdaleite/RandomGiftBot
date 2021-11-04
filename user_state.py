from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class InitialState(StatesGroup):
    waiting_for_accept = State()
    waiting_for_settings = State()

class WishlistState(StatesGroup):
    managing_wishlist = State()
    adding_wish = State()
    removing_wish = State()

class MessagingState(StatesGroup):
    messaging = State()
    sending_message_to_grandson = State()
    sending_message_to_santa = State()

class ManageGameState(StatesGroup):
    joining_or_creating_game = State()
    joining_game = State()
    creating_game = State()
    leader_waiting_state = State()
    adding_user = State()
    choosing_group = State()
    choosing_user = State()
    starting_game = State()
