from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = [
    [InlineKeyboardButton(text='Поиск кроссовок Nike', callback_data='gns_btn'),
     InlineKeyboardButton(text='Поиск по URL', callback_data='url_btn')],
    [InlineKeyboardButton(text='Режим уведомлений', callback_data='notif_btn')],
    [InlineKeyboardButton(text='Информация о боте', callback_data='inf_btn')]
]

main = InlineKeyboardMarkup(inline_keyboard=main_kb)

to_main_kb = [
    [InlineKeyboardButton(text='К главному меню', callback_data='to_main_btn')]
]

to_main = InlineKeyboardMarkup(inline_keyboard=to_main_kb)

off_notif_kb = [
    [InlineKeyboardButton(text='Отключить режим уведомлений', callback_data='off_btn')]
]

off_notif = InlineKeyboardMarkup(inline_keyboard=off_notif_kb)
