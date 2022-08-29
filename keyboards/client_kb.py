from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('Ассортимент 🍷')
b2 = KeyboardButton('Расположение 🏙')
b3 = KeyboardButton('Режим работы 📆')
b4 = KeyboardButton('Контакты ☎️')
b5 = KeyboardButton('Корзина 🛒')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.add(b1)
kb_client.add(b2, b3, b4)
kb_client.add(b5)

b6 = KeyboardButton("📞 Оставить номер", request_contact=True)
kb_phone = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_phone.add(b6)
