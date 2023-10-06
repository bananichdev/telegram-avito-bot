import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Filter, StateFilter
from app.keyboards import main, to_main, off_notif
from app.parser import AvitoParse
import validators
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
router = Router()
stop_send_notifications = False
stop_send_messages = False


class FSMSearch(StatesGroup):
    pages = State()
    url = State()


class FSMNotification(StatesGroup):
    notification = State()


class PagesValidator(Filter):
    async def __call__(self, message: Message):
        return message.text.isdigit() and 1 <= int(message.text) <= 100


async def send_results(cards_obj: AvitoParse, message: Message):
    global stop_send_messages
    stop_send_messages = False
    cards = await asyncio.to_thread(cards_obj.parse)
    for card in cards:
        if stop_send_messages:
            break
        await message.answer(
            f'Название: {card["name"]}\n'
            f'Цена: {card["price"]}\n'
            f'Описание: {card["description"]}\n'
            f'URL: {card["url"]}'
        )
        await message.answer(
            text='Если хотите остановить отправку, то нажмите кнопку',
            reply_markup=to_main
        )
        await asyncio.sleep(5)
    else:
        await message.answer(
            text='Можете дальше пользоваться ботом',
            reply_markup=main
        )


@router.message(F.text == '/start')
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text='Помогу найти <b><em>оригинальные</em></b> вещи на Авито',
        parse_mode='html',
        reply_markup=main
    )


'''****************************start****************************'''


@router.callback_query(F.data.in_({'gns_btn', 'url_btn'}))
async def gns_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMSearch.pages)
    await state.update_data(command=callback.data.split('_')[0])
    try:
        await callback.message.delete()
        await callback.message.answer(
            text='Введите количество страниц, на которых будут искаться объявления\n'
                 '<b>Число от 1 до 100</b>',
            parse_mode='html',
            reply_markup=to_main
        )
    except Exception as e:
        logging.error(f'Error: {e}', exc_info=True)
        await callback.message.edit_text(
            text='Введите количество страниц, на которых будут искаться объявления\n'
                 '<b>Число от 1 до 100</b>',
            parse_mode='html',
            reply_markup=to_main
        )


'''****************************start****************************'''

'''****************************pages****************************'''


@router.message(FSMSearch.pages, PagesValidator())
async def pages(message: Message, state: FSMContext):
    count_pages = int(message.text)
    data = await state.get_data()
    if data['command'] == 'url':
        await state.update_data(count_pages=count_pages)
        await state.set_state(FSMSearch.url)
        await message.answer(
            text='Теперь введите URL Авито страницы, на который будут искаться объявления',
            reply_markup=to_main
        )
    else:
        await state.clear()
        await message.answer(
            text='Поиск вещей...\n'
                 'Немного подождите'
        )
        await message.answer(
            text='<b>Ничего не пишите до окончания работы бота!</b>',
            parse_mode='html'
        )
        cards_obj = AvitoParse(url='https://www.avito.ru/all/odezhda_obuv_aksessuary/obuv_muzhskaya-ASgBAgICAUTeArqp1gI?cd=1&f=ASgBAQECAUTeArqp1gICQOK8DTS8q9YC8NE07tE0uIcO1ObykwHk8pMB4vKTAeDykwHe8pMB3PKTAdrykwHY8pMB1vKTAdTykwHS8pMB0PKTAc7ykwEBRcaaDBd7ImZyb20iOjUwMCwidG8iOjE1MDAwfQ&q=%D0%BA%D1%80%D0%BE%D1%81%D1%81%D0%BE%D0%B2%D0%BA%D0%B8+nike+%D0%BE%D1%80%D0%B8%D0%B3%D0%B8%D0%BD%D0%B0%D0%BB&s=104', count=count_pages)
        await send_results(cards_obj, message)


'''****************************pages****************************'''

'''*****************************url*****************************'''


@router.message(FSMSearch.url, F.text.func(lambda text: 'avito.ru/' in text and validators.url(text)))
async def url(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await message.answer(
        text='Поиск вещей...'
             '\nНемного подождите'
    )
    await message.answer(
        text='<b>Ничего не пишите до окончания работы бота!</b>',
        parse_mode='html'
    )
    cards_obj = AvitoParse(url=message.text, count=data['count_pages'])
    await send_results(cards_obj, message)


'''*****************************url*****************************'''

'''****************************notif****************************'''


@router.callback_query(F.data == 'notif_btn')
async def notif_callback(callback: CallbackQuery, state: FSMContext):
    global stop_send_notifications
    stop_send_notifications = False
    try:
        await callback.message.delete()
        await callback.message.answer(
            text='Введите URL Авито страницы\n'
                 'Если хотите получать уведомления о новых объявлениях кроссовок Nike, то введите 0',
            reply_markup=to_main
        )
    except Exception as e:
        logging.error(f'Error: {e}', exc_info=True)
        await callback.message.edit_text(
            text='Введите URL Авито страницы\n'
                 'Если хотите получать уведомления о новых объявлениях кроссовок Nike, то введите 0',
            reply_markup=to_main
        )
    finally:
        await state.set_state(FSMNotification.notification)


@router.message(FSMNotification.notification, F.text.func(lambda text: 'avito.ru/' in text or text == '0'))
async def notifications(message: Message, state: FSMContext):
    await message.answer(
        text='Режим уведомлений включен',
        reply_markup=off_notif
    )
    await state.clear()
    if message.text == '0':
        notif_obj = AvitoParse(url='https://www.avito.ru/all/odezhda_obuv_aksessuary/obuv_muzhskaya-ASgBAgICAUTeArqp1gI?cd=1&f=ASgBAQECAUTeArqp1gICQOK8DTS8q9YC8NE07tE0uIcO1ObykwHk8pMB4vKTAeDykwHe8pMB3PKTAdrykwHY8pMB1vKTAdTykwHS8pMB0PKTAc7ykwEBRcaaDBd7ImZyb20iOjUwMCwidG8iOjE1MDAwfQ&q=%D0%BA%D1%80%D0%BE%D1%81%D1%81%D0%BE%D0%B2%D0%BA%D0%B8+nike+%D0%BE%D1%80%D0%B8%D0%B3%D0%B8%D0%BD%D0%B0%D0%BB&s=104')
    else:
        notif_obj = AvitoParse(url=message.text)
    await asyncio.to_thread(notif_obj.set_up)
    count_notif = 0
    global stop_send_notifications
    while True:
        if stop_send_notifications:
            await asyncio.to_thread(notif_obj.quit)
            break
        if count_notif == 0:
            notif = await asyncio.to_thread(notif_obj.notifications)
            if notif is not None:
                count_notif += 1
                await message.answer(
                    f'Название: {notif["name"]}\n'
                    f'Цена: {notif["price"]}\n'
                    f'Описание: {notif["description"]}\n'
                    f'URL: {notif["url"]}'
                )
            await asyncio.sleep(5)
        else:
            new_notif = await asyncio.to_thread(notif_obj.notifications)
            if new_notif != notif and new_notif is not None:
                count_notif += 1
                notif = new_notif
                await message.answer(
                    f'Название: {notif["name"]}\n'
                    f'Цена: {notif["price"]}\n'
                    f'Описание: {notif["description"]}\n'
                    f'URL: {notif["url"]}'
                )
                await message.answer(
                    text='Если хотите выключить режим уведомлений, то нажмите кнопку',
                    reply_markup=off_notif
                )
            await asyncio.sleep(5)


'''****************************notif****************************'''

'''*************************invalid_data************************'''


@router.message(StateFilter(FSMNotification.notification, FSMSearch.url))
async def invalid_url(message: Message):
    await message.answer(
        text='<b>Некорректные данные!\n'
             'Введите URL Авито страницы</b>',
        parse_mode='html',
        reply_markup=to_main
    )


@router.message(FSMSearch.pages)
async def invalid_pages(message: Message):
    await message.answer(
        text='<b>Некорректные данные!\n'
             'Введите число от 1 до 100</b>',
        parse_mode='html',
        reply_markup=to_main
    )


'''*************************invalid_url*************************'''

'''*****************************inf*****************************'''


@router.callback_query(F.data == 'inf_btn')
async def inf_callback(callback: CallbackQuery):
    try:
        await callback.message.delete()
        await callback.message.answer(
            text='Алгоритм данного бота рассчитан на поиск <em>оригинальных вещей</em>\n'
                 'Однако, пока что, бот может находить сомнительные предложения(даркреселлеров)\n'
                 'Но все-же большинство объявлений - оригинальные вещи\n\n\n'
                 'Описание возможностей:\n\n'
                 'Поиск кроссовок Nike - ищет объявления с кроссовками Nike\n\n'
                 'Поиск по URL - ищет объявления по заданному URL\n\n'
                 'Режим уведомлений - ищет самые новые объявления по заданному URL\n\n\n'
                 'По вопросам сотрудничества и улучшения функционала писать сюда: @vzlomjopii',
            parse_mode='html',
            reply_markup=to_main
        )
    except Exception as e:
        logging.error(f'Error: {e}', exc_info=True)
        await callback.message.edit_text(
            text='Алгоритм данного бота рассчитан на поиск <em>оригинальных вещей</em>\n'
                 'Однако, пока что, бот может находить сомнительные предложения(даркреселлеров)\n'
                 'Но все-же большинство объявлений - оригинальные вещи\n\n\n'
                 'Описание возможностей:\n\n'
                 'Поиск кроссовок Nike - ищет объявления с кроссовками Nike\n\n'
                 'Поиск по URL - ищет объявления по заданному URL\n\n'
                 'Режим уведомлений - ищет самые новые объявления по заданному URL\n\n\n'
                 'По вопросам сотрудничества и улучшения функционала писать сюда: @vzlomjopii',
            parse_mode='html',
            reply_markup=to_main
        )


'''*****************************inf*****************************'''

'''***************************to_main***************************'''


@router.callback_query(F.data.in_({'to_main_btn', 'off_btn'}))
async def to_main_callback(callback: CallbackQuery, state: FSMContext):
    global stop_send_messages
    global stop_send_notifications
    if callback.data == 'off_btn':
        stop_send_notifications = True
    else:
        stop_send_messages = True
    await state.clear()
    try:
        await callback.message.delete()
        await callback.message.answer(
            text='Помогу найти <b><em>оригинальные</em></b> вещи на Авито',
            parse_mode='html',
            reply_markup=main
        )
    except Exception as e:
        logging.error(f'Error: {e}', exc_info=True)
        await callback.message.edit_text(
            text='Помогу найти <b><em>оригинальные</em></b> вещи на Авито',
            parse_mode='html',
            reply_markup=main
        )


'''***************************to_main***************************'''

'''****************************other****************************'''


@router.message()
async def other(message: Message):
    await message.answer(
        text='Я вас не понимаю...'
    )


'''****************************other****************************'''
