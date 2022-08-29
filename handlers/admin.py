import asyncio
import random

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import config
from create_bot import dp, bot
from data_base.sqlite_db import *
from keyboards import admin_kb
from states.admin import FSMAdmin
from states.mail import FSMMail


async def mailing(photo, text):
    g, e = 0, 0
    for user in Users.select():
        try:
            await bot.send_photo(user.id, photo, text, parse_mode='html')
            g += 1
        except:
            try:
                await bot.send_message(user.id, text, parse_mode='html')
                g += 1
            except:
                e += 1


def between_callback(photo, text):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(mailing(photo, text))
    loop.close()


# Получаем айди админа/модератора
async def make_changes_command(message: types.Message):
    if message.from_user.id in config.admins:
        await bot.send_sticker(message.from_user.id,
                               'CAACAgEAAxkBAAEFmpxi_0jzvA9Iv9PMDPLwMvitTitZYAACIwkAAuN4BAABn1mg9roZ0DkpBA')
        await bot.send_message(message.from_user.id, '🔓 *Вы вошли в панель модератора\!*',
                               reply_markup=admin_kb.button_case_admin)
        await message.delete()


# Начало диалога загрузки нового пункта меню
async def cm_start(message: types.Message):
    if message.from_user.id in config.admins:
        await FSMAdmin.photo.set()
        await bot.send_message(message.from_user.id, '📷 *Загрузите фото*')


# Ловим первый ответ и пишем в словарь
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, '📃 *Введите название*')


# Ловим второй ответ
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, '📝 *Введите описание*')


# Ловим третий ответ
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await bot.send_message(message.from_user.id, '🏷 *Теперь укажите цену*')


# Ловим четвертый ответ и используем все полученные данные
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['price'] = float(message.text)

            Products.create(id=random.randint(11111111, 99999999), photo=data['photo'], name=data['name'],
                            description=data['description'], price=data['price'])
            await bot.send_photo(
                message.from_user.id, data["photo"],
                f'📃 *Название:* {data["name"]}\n🏷 *Цена:* {data["price"]} RUB\n📝 *Описание:*\n{data["description"]}'.replace('.', '\.'),
                parse_mode=None
            )
        await state.finish()


async def cancel_handler(message: types.Message):
    if message.from_user.id in config.admins:
        sql = Products.select()

        kb = InlineKeyboardMarkup(row_width=2)
        [kb.add(InlineKeyboardButton(text=product.name, callback_data='delete_' + str(product))) for product in sql]
        await bot.send_message(message.from_user.id, '❌ *Выберите продукт для удаления:*', reply_markup=kb)


async def mail(message: types.Message):
    if message.from_user.id in config.admins:
        await FSMMail.photo.set()
        button_load = KeyboardButton('Пропуск')

        kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load)
        await bot.send_message(message.from_user.id, '📷 *Загрузите фото рассылки*', reply_markup=kb)


@dp.message_handler(content_types=['photo'], state=FSMMail.photo)
async def mail2(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            try:
                data['photo'] = message.photo[0].file_id
            except:
                data['photo'] = None

        await FSMMail.next()
        await bot.send_message(message.from_user.id, '✉️ *Теперь введите текст рассылки*')


@dp.message_handler(state=FSMMail.description)
async def mail3(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['description'] = message.text

            g, e = 0, 0
            for user in Users.select():
                try:
                    await bot.send_photo(user.id, data['photo'], data['description'], parse_mode='html')
                    g += 1
                except:
                    try:
                        await bot.send_message(user.id, data['description'], parse_mode='html')
                        g += 1
                    except:
                        e += 1

        await state.finish()
        await bot.send_message(message.from_user.id, f'👍 *Получили сообщение:* {g}\n👎 *Не получили:* {e}',
                               reply_markup=admin_kb)


# Регистрируем хендлеры
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, text=['📥 Добавить товар'], state=None)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_message_handler(cancel_handler, text=['❌ Удалить товар'], state=None)
    dp.register_message_handler(mail, text=['🔊 Рассылка'], state=None)
    dp.register_message_handler(make_changes_command, commands=['moderator'], state='*')
