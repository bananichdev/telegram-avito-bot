import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Filter, StateFilter
from app.keyboards import main, to_main, off_notif
from app.parser import AvitoParse

router = Router()
stop_send_messages = False


class FSMSearch(StatesGroup):
    pages = State()
    url = State()


class FSMNotification(StatesGroup):
    notification = State()


class PagesValidator(Filter):
    async def __call__(self, message: Message):
        return message.text.isdigit() and 1 <= int(message.text) <= 100


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
    await callback.message.delete()
    await callback.message.answer(
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
        cards = await asyncio.to_thread(AvitoParse(url='https://clck.ru/35o5vb', count=count_pages).parse)
        for card in cards:
            await message.answer(
                f'Название: {card["name"]}\n'
                f'Цена: {card["price"]}\n'
                f'Описание: {card["description"]}\n'
                f'URL: {card["url"]}'
            )
            await asyncio.sleep(2)
        await message.answer(
            text='Можете дальше пользоваться ботом',
            reply_markup=main
        )


'''****************************pages****************************'''

'''*****************************url*****************************'''


@router.message(FSMSearch.url, F.text.func(lambda text: 'avito.ru/' in text))
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
    cards = await asyncio.to_thread(AvitoParse(url=message.text, count=data['count_pages']).parse)
    for card in cards:
        await message.answer(
            f'Название: {card["name"]}\n'
            f'Цена: {card["price"]}\n'
            f'Описание: {card["description"]}\n'
            f'URL: {card["url"]}'
        )
        await asyncio.sleep(2)
    await message.answer(
        text='Можете дальше пользоваться ботом',
        reply_markup=main
    )


'''*****************************url*****************************'''

'''****************************notif****************************'''


@router.callback_query(F.data == 'notif_btn')
async def notif_callback(callback: CallbackQuery, state: FSMContext):
    global stop_send_messages
    stop_send_messages = False
    await callback.message.delete()
    await state.set_state(FSMNotification.notification)
    await callback.message.answer(
        text='Введите URL Авито страницы\n'
             'Если хотите получать уведомления о новых объявлениях кроссовок Nike, то введите 0',
        reply_markup=to_main
    )


@router.message(FSMNotification.notification, F.text.func(lambda text: 'avito.ru/' in text or text == '0'))
async def notifications(message: Message, state: FSMContext):
    await message.answer(
        text='Режим уведомлений включен',
        reply_markup=off_notif
    )
    await state.clear()
    if message.text == '0':
        notif_obj = AvitoParse(url='https://clck.ru/35o5vb')
    else:
        notif_obj = AvitoParse(url=message.text)
    await asyncio.to_thread(notif_obj.set_up)
    count_notif = 0
    global stop_send_messages
    while True:
        if stop_send_messages:
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


'''*****************************inf*****************************'''

'''***************************to_main***************************'''


@router.callback_query(F.data.in_({'to_main_btn', 'off_btn'}))
async def to_main_callback(callback: CallbackQuery, state: FSMContext):
    global stop_send_messages
    stop_send_messages = True
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
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
