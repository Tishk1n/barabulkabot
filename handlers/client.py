from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from create_bot import bot
from data_base.sqlite_db import *
from keyboards import kb_client, kb_phone
from states.order import FSMZakazat


async def command_start(message: types.Message):
    base = Users.get_or_none(Users.id == message.from_user.id)

    await bot.send_sticker(message.from_user.id,
                           'CAACAgIAAxkBAAEFmbxi_mQLsxaVWhHPyhKCr2ZeCvlGmgACKAADKA9qFJBLt8sebwMQKQQ')
    if base is None:
        Users.create(id=message.from_user.id)
        await bot.send_message(message.from_user.id,
                               '👋 *Добро пожаловать\!*\n\nМы — профессионалы в винном деле и решили для удобства '
                               'открыть свои филиалы во всеми любимом Telegram\!',
                               reply_markup=kb_client)
    else:
        await bot.send_message(message.from_user.id, '👋 *С возвращением\!*', reply_markup=kb_client)


async def pizza_open_commmand(message: types.Message):
    await bot.send_sticker(message.from_user.id,
                           'CAACAgEAAxkBAAEFmqdi_0sz-Cb-PVM2q8cm6apEyaJBHAACxQEAAkpieUUwa86ewMXfASkE')
    await bot.send_message(message.from_user.id, '🥰 *Пн\-Пт: 11:00 до 22:00*')


async def pizza_place_commmand(message: types.Message):
    await bot.send_sticker(message.from_user.id,
                           'CAACAgEAAxkBAAEFmqBi_0on_nzuaT5wLDGVyzRm0xYGagACfQIAAjPfcUW7Yzvacs97JCkE')
    await bot.send_message(message.from_user.id, 'Москва, ул\. Красносельская Нижняя, д\. 35, стр\. 5, помещение 7')


async def pizza_tel_commmand(message: types.Message):
    await bot.send_sticker(message.from_user.id,
                           'CAACAgEAAxkBAAEFmp5i_0lD3MUFYbExV-0OIR4n_F4AARYAAhoCAAIde6FGQHoZrVFtNN8pBA')
    await bot.send_message(message.from_user.id, '☎️ *Наши телефоны: \n\+79884014330 \n\n\+79852555176*')


async def pizza_menu_command(message: types.Message):
    sql = Products.select().execute()

    kb = InlineKeyboardMarkup(row_width=2)
    [kb.add(InlineKeyboardButton(text=product.name, callback_data='product_' + str(product.id))) for product in sql]
    await bot.send_message(message.from_user.id, '🍷 *Ассортимент товаров:*', reply_markup=kb)


async def pizza_cart_command(message: types.Message):
    sql = Orders.select().where(Orders.user_id == message.from_user.id).execute()

    kb = InlineKeyboardMarkup(row_width=2)
    for order in sql:
        product = Products.get(Products.id == int(order.product_id))
        kb.add(InlineKeyboardButton(text=product.name, callback_data='order_' + str(order.product_id)))

    kb.add(InlineKeyboardButton(text='✅ Подтвердить оплату', callback_data='cart_confirm'))

    await bot.send_message(message.from_user.id, '🛒 *Ваша корзина:*', reply_markup=kb)


async def handler_call(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('product_'):
        product = Products.get(Products.id == int(call.data.split('product_', maxsplit=1)[1]))

        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton(text=f'💳 Добавить в корзину',
                                    callback_data=f'cart_' + call.data.split('product_', maxsplit=1)[1]))
        kb.add(InlineKeyboardButton(text=f'❌ Отменить', callback_data=f'cancel'))
        await call.message.delete()
        await bot.send_photo(call.from_user.id, product.photo,
                             f'📃 *Название:* {product.name}\n🏷 *Цена:* {product.price} RUB\n📝 *Описание:*\n{product.description}'.replace('.', '\.'),
                             reply_markup=kb)

    elif call.data.startswith('cart_') and not call.data.startswith('cart_count_') and not call.data.startswith(
            'cart_confirm'):
        Orders.create(user_id=call.from_user.id, product_id=int(call.data.split('cart_', maxsplit=1)[1]), count=1,
                      status=3)
        await call.answer(text=f'✅ Товар добавлен в корзину! Чтобы выбрать количество перейдите в её.')
        await call.message.delete()

    elif call.data.startswith('order_'):
        order = Orders.get(Orders.product_id == int(call.data.split('order_', maxsplit=1)[1]),
                           Orders.user_id == call.from_user.id)
        product = Products.get(Products.id == order.product_id)

        kb = InlineKeyboardMarkup(row_width=3)
        kb.add(InlineKeyboardButton(text=f' ', callback_data=f'space'),
               InlineKeyboardButton(text=f'🔝', callback_data=f'cart'),
               InlineKeyboardButton(text=f' ', callback_data=f'space'))
        kb.add(InlineKeyboardButton(text=f'🔺', callback_data=f'cart_count_' + str(order.product_id) + '_+1'),
               InlineKeyboardButton(text=f'1', callback_data=f'1'),
               InlineKeyboardButton(text=f'🔻', callback_data=f'cart_count_' + str(order.product_id) + '_-1'))
        kb.add(InlineKeyboardButton(text=f'🔺', callback_data=f'cart_count_' + str(order.product_id) + '_+10'),
               InlineKeyboardButton(text=f'10', callback_data=f'10'),
               InlineKeyboardButton(text=f'🔻', callback_data=f'cart_count_' + str(order.product_id) + '_-10'))
        kb.add(InlineKeyboardButton(text=f' ', callback_data=f'space'),
               InlineKeyboardButton(text=f'❌', callback_data=f'cancel_order_' + str(order.product_id)),
               InlineKeyboardButton(text=f' ', callback_data=f'space'))
        await call.message.delete()
        await bot.send_photo(call.from_user.id, product.photo,
                             f'📃 *Название:* {product.name}\n🏷 *Цена:* {product.price} RUB\n📦 *Количество к покупке:* {order.count}\n📝 *Описание:*\n{product.description}'.replace('.', '\.'),
                             reply_markup=kb)

    elif call.data.startswith('cart_count_'):
        order = Orders.get(Orders.product_id == int(call.data.split('cart_count_', maxsplit=1)[1].split('_')[0]),
                           Orders.user_id == call.from_user.id)
        order.count = eval(
            'order.count ' + call.data.split('cart_count_', maxsplit=1)[1].split('_')[1] + ' if order.count ' +
            call.data.split('cart_count_', maxsplit=1)[1].split('_')[1] + ' > 0 else 1')
        order.save()
        product = Products.get(Products.id == order.product_id)

        kb = InlineKeyboardMarkup(row_width=3)
        kb.add(InlineKeyboardButton(text=f'🔺', callback_data=f'cart_count_' + str(order.product_id) + '_+1'),
               InlineKeyboardButton(text=f'1', callback_data=f'1'),
               InlineKeyboardButton(text=f'🔻', callback_data=f'cart_count_' + str(order.product_id) + '_-1'))
        kb.add(InlineKeyboardButton(text=f'🔺', callback_data=f'cart_count_' + str(order.product_id) + '_+10'),
               InlineKeyboardButton(text=f'10', callback_data=f'10'),
               InlineKeyboardButton(text=f'🔻', callback_data=f'cart_count_' + str(order.product_id) + '_-10'))
        kb.add(InlineKeyboardButton(text=f' ', callback_data=f'space'),
               InlineKeyboardButton(text=f'❌', callback_data=f'cancel_order_' + str(order.product_id)),
               InlineKeyboardButton(text=f' ', callback_data=f'space'))
        await call.message.delete()
        await bot.send_photo(call.from_user.id, product.photo,
                             f'📃 *Название:* {product.name}\n🏷 *Цена:* {product.price} RUB\n📦 *Количество к покупке:* {order.count}\n📝 *Описание:*\n{product.description}'.replace('.', '\.'),
                             reply_markup=kb)

    elif call.data.startswith('cancel_order_'):
        Orders.delete().where(Orders.product_id == int(call.data.split('cancel_order_', maxsplit=1)[1]),
                              Orders.user_id == call.from_user.id).execute()
        await call.answer(text=f'✅ Продукт удалён из корзины.')
        await call.message.delete()

    elif call.data.startswith('delete_'):
        if call.from_user.id in config.admins:
            Products.delete().where(Products.id == int(call.data.split('delete_', maxsplit=1)[1])).execute()
            await call.answer(text=f'✅ Продукт удалён.')
            await call.message.delete()

    elif call.data.startswith('confirm_'):
        if call.from_user.id in config.admins:
            Orders.delete().where(Orders.user_id == int(call.data.split('confirm_', maxsplit=1)[1])).execute()
            await call.answer(text=f'✅ Заказ подтверждён.')
            await bot.send_message(int(call.data.split('confirm_', maxsplit=1)[1]), '✅ *Ваш заказ принят\!*')

    elif call.data.startswith('unconfirm_'):
        if call.from_user.id in config.admins:
            Orders.delete().where(Orders.user_id == int(call.data.split('unconfirm_', maxsplit=1)[1])).execute()
            await call.answer(text=f'✅ Заказ отклонён.')
            await bot.send_message(int(call.data.split('confirm_', maxsplit=1)[1]), '❌ *Ваш заказ был отклонён!*')

    elif call.data == 'cancel':
        await call.answer(text=f'✅ Успешно!')
        await call.message.delete()

    elif call.data == 'cart':
        await call.message.delete()

    elif call.data == 'cart_confirm':
        sql = Orders.select().where(Orders.user_id == call.from_user.id).execute()

        text = ''
        total = 0.0

        for order in sql:
            product = Products.get(Products.id == int(order.product_id))
            order_price = product.price * order.count
            text += f'\n• {product.name} \({order.count} шт.\) \— {order_price} RUB'

            total += order_price

        if len(sql) > 0:
            await call.message.delete()

            await bot.send_message(call.from_user.id, f'🛍 *К покупке:*\n{text}\n\n*Итого:* {total} RUB'.replace('.', '\.'))
            await bot.send_message(call.from_user.id, f'📲 *Для продожнения, поделитесь своим номером*',
                                   reply_markup=kb_phone)

            await FSMZakazat.phone.set()

        else:
            await call.answer(text=f'Корзина пуста 😔')


async def pizza_count(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['cont'] = message.contact.phone_number

        sql = Orders.select().where(Orders.user_id == message.from_user.id).execute()

        text = ''
        total = 0.0

        for order in sql:
            product = Products.get(Products.id == int(order.product_id))
            order_price = product.price * order.count
            text += f'\n• {product.name} ({order.count} шт.) — {order_price} RUB'

            total += order_price

        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton(text=f'✅ Подвердить', callback_data=f'confirm_' + str(message.from_user.id)))
        kb.add(InlineKeyboardButton(text=f'❌ Отклонить', callback_data=f'unconfirm_' + str(message.from_user.id)))

        [await bot.send_message(id,
                                f'📩 <b>Новый заказ!\n🙎‍♂️ Пользователь:</b> {message.from_user.mention}\n{text}\n\n'
                                f'<b>Итого:</b> {total} RUB\n<b>☎️ Телефон:</b> {data["cont"]}',
                                parse_mode='html', reply_markup=kb) for id in config.admins]

    await state.finish()
    await bot.send_sticker(message.from_user.id,
                           'CAACAgEAAxkBAAEFmqti_05DWW1Le-6jl03F5yi3_BPB5gACvAIAAuL8qUZrkJT2k8fvRikE')
    await bot.send_message(message.from_user.id, '✅ *Заявка успешно отправлена\. Ожидайте звонок от менеджера\!*',
                           reply_markup=kb_client)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_start, text=['🔝 Назад в меню'])
    dp.register_message_handler(pizza_open_commmand, text=['Режим работы 📆'])
    dp.register_message_handler(pizza_place_commmand, text=['Расположение 🏙'])
    dp.register_message_handler(pizza_tel_commmand, text=['Контакты ☎️'])
    dp.register_message_handler(pizza_menu_command, text=['Ассортимент 🍷'])
    dp.register_message_handler(pizza_cart_command, text=['Корзина 🛒'])
    dp.register_message_handler(pizza_count, content_types=['contact'], state=FSMZakazat.phone)
    dp.register_callback_query_handler(handler_call)
