from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

button_load = KeyboardButton('📥 Добавить товар')
button_delete = KeyboardButton('❌ Удалить товар')
button_mail = KeyboardButton('🔊 Рассылка')
button_back = KeyboardButton('🔝 Назад в меню')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True)\
    .add(button_load, button_delete)\
    .add(button_mail)\
    .add(button_back)
