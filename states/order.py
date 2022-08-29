from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMZakazat(StatesGroup):
    phone = State()
