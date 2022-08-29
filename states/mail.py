from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMMail(StatesGroup):
    photo = State()
    description = State()
