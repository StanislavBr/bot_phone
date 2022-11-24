import logging
from aiogram import Bot, Dispatcher, executor, types
from function import generate_user_stats, format_numbers, get_current_date
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from sqlighter import SQLighter
import datetime
from keyboard import *
from zadarma import api
import asyncio
import ast

with open('active_account.txt', 'r') as file:
    api_data = file.read()

# kk = 'c978434c60ca068c586a' TEST
# ck = '392c3e4cddedb97f0ec8' TEST
kk = api_data.split('|')[0]
ck = api_data.split('|')[1]

api = api.ZadarmaAPI(key=f'{kk}', secret=f'{ck}')
db = SQLighter('db.db')
# bot = Bot(token="5753137797:AAGIAXOnCVImtGlSPELaQHPBdUk0T2wAbHk") TEST
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
# admin_id = [1158936386] TEST
errors = {'busy': 'Занято', 'cancel': 'Отменен', 'no answer': 'Без ответа', 'failed': 'Не удался',
          'unallocated number': 'Номер не существует'}


chat_admins = -671959464


class AddAccount(StatesGroup):
    value = State()


@dp.message_handler(commands='stats')
async def _(message: types.Message):
    if message.chat.id in [chat_admins]:
        db.delete_last_stats(get_current_date())
        current_dates = datetime.datetime.now()
        text = f"📝<b>Статистика звонков за {current_dates.day}/{current_dates.month}</b>\n\n"
        for i in db.get_all_stats_data():
            text += f"🆔 - @{i[3]} (<code>{i[0]}</code>) <b>совершено звонков --- {i[1]}</b>\n\n"
        await message.reply(text, parse_mode='html')


@dp.message_handler(commands='admin')
async def _(message: types.Message):
    if message.from_user.id in admin_id:
        if db.check_user(message.from_user.id) is not None:
            await message.answer(
                "Меню аккаунтов:",
                reply_markup=admin_service_key(),
                parse_mode='html'
            )
        else:
            await message.answer("Вас нет в базе пропишите /start и зарегистрируйтесь")


@dp.callback_query_handler(text_startswith='delete_acc')
async def _(query: types.CallbackQuery, state: FSMContext):
    data = query.data.split('|')
    db.delete_accounts(data[1])
    await bot.send_message(
        chat_id=query.from_user.id,
        text=f'Аккаунт удален!\n\n<code>{data[1]}\n{data[2]}</code>',
        parse_mode='html'
    )


@dp.callback_query_handler(text_startswith='set_account')
async def _(query: types.CallbackQuery, state: FSMContext):
    data = query.data.split('|')
    with open('active_account.txt', 'w', encoding='utf8') as file:
        file.write(f'{data[1]}|{data[2]}')
    await bot.delete_message(
        chat_id=query.from_user.id,
        message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text='Все доступные аккаунт:',
        reply_markup=accounts_keyboard()
    )


@dp.callback_query_handler(state='*', text_startswith='cancelling')
async def _(query: types.CallbackQuery, state: FSMContext):
    if db.check_user(query.message.from_user.id) is not None:
        await bot.send_message(
            chat_id=query.from_user.id,
            text='Отменено'
        )
        await state.finish()
    else:
        await query.message.answer('Вас нет в базе пропишите /start и подайте заявку повторно')


@dp.callback_query_handler(text_startswith='add_account')
async def _(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id in admin_id:
        await query.message.answer(
            "Укажите данные аккаунт через пробел\n\nПример: (key secret)",
            reply_markup=cancel_acc()
        )
        await AddAccount.value.set()


@dp.message_handler(state=AddAccount.value)
async def _(message: types.Message, state: FSMContext):
    if message.text in ['start', 'test']:
        await message.answer("No!")
    else:
        msg = message.text.split(' ')
        db.write_account(msg[0], msg[1])
        await message.answer(
            f"Успешно добавлен аккаунт!\nkey = {msg[0]}\nsecret = {msg[1]}",
            reply_markup=admin_service_key()
        )
        await state.finish()


@dp.callback_query_handler(text_startswith='show_account')
async def _(query: types.CallbackQuery):
    if query.from_user.id in admin_id:
        await query.message.answer("Все доступные аккаунты: ", reply_markup=accounts_keyboard())


@dp.message_handler(commands="start")
async def _(message: types.Message):
    print(message)
    if not db.user_exists(message.from_user.id):
        db.user_add(message.from_user.id)
    if datetime.datetime.now() < db.get_date_subs(message.from_user.id) or db.get_count_call(message.from_user.id) > 0:
        await message.reply('Добро пожаловать в главное меню!', reply_markup=keyboard_menu(message.from_user.id))
    else:
        await message.reply('У вас нет доступа!\nДля получения доступа, нажмите на кнопку ниже',
                            reply_markup=keyboard_registration)


@dp.callback_query_handler(text='profile')
async def _(message: types.CallbackQuery):
    if db.check_user(message.from_user.id) is not None:
        if not db.user_exists(message.from_user.id):
            await message.message.answer(
                f"Подписка до: {db.get_date_subs(message.from_user.id).strftime('%d.%m.%Y')}" + '\n' + f'Кол-во звонков: {db.get_count_call(message.from_user.id)}')
    else:
        await message.message.answer('Вас нет в базе. Пропишите /start и подайте заявку снова')


@dp.message_handler(commands='get_id')
async def _(message: types.Message):
    await message.reply(f'{message.chat.id}')


@dp.callback_query_handler(text='registr')
async def _(message: types.CallbackQuery):
    if datetime.datetime.now() < db.get_date_subs(message.from_user.id):
        pass
    else:
        db.update_logic(message.from_user.id, 'registr')
        await message.message.answer(
            'Напишите свою заявку администрации(все что вы напишите,автоматически отправится администрации на рассмотрение)')


@dp.callback_query_handler(text='call')
async def _(message: types.CallbackQuery):
    if db.check_user(message.from_user.id) is not None:
        if datetime.datetime.now() < db.get_date_subs(message.from_user.id) or db.get_count_call(
            message.from_user.id) > 0:
            db.update_logic(message.from_user.id, 'phone_number')
            await message.message.answer('Введите номер в любом удобном формате:\n +7999, 8999, 8-999',
                                         reply_markup=keyboard_back)
        else:
            await message.message.answer('У вас нет доступа!', reply_markup=keyboard_registration)
    else:
        await message.message.answer('Вас нет в базе. Пропишите /start и подайте заявку снова')


@dp.callback_query_handler(text='back')
async def _(message: types.CallbackQuery):
    if db.check_user(message.from_user.id) is not None:
        db.update_logic(message.from_user.id, '')
        db.update_phone_number(message.from_user.id, '')
        await message.message.answer('Добро пожаловать в главное меню!',
                                     reply_markup=keyboard_menu(message.from_user.id))
    else:
        await message.message.answer('Вас нет в базе. Пропишите /start и подайте заявку снова')


@dp.callback_query_handler(text='add_subs')
async def _(message: types.CallbackQuery):
    if db.check_user(message.from_user.id) is not None:
        db.update_logic(message.from_user.id, 'add_subs')
        await message.message.answer('Введите id пользователя', reply_markup=keyboard_back)
    else:
        await message.message.answer('Вас нет в базе. Пропишите /start и подайте заявку снова')


@dp.callback_query_handler(text='del_subs')
async def _(message: types.CallbackQuery):
    if db.check_user(message.from_user.id) is not None:
        db.update_logic(message.from_user.id, 'del_subs')
        await message.message.answer('Введите id пользователя', reply_markup=keyboard_back)
    else:
        await message.message.answer('Вас нет в базе. Пропишите /start и подайте заявку снова')


@dp.callback_query_handler(text='days')
async def _(message: types.CallbackQuery):
    if db.check_user(message.from_user.id) is not None:
        db.update_logic(message.from_user.id, f'days:{db.get_logic(message.from_user.id)}')
        await bot.delete_message(chat_id=chat_admins, message_id=message.message.message_id)
        await message.message.answer('Введите кол-во дней')
    else:
        await message.message.answer('Вас нет в базе. Пропишите /start и подайте заявку снова')


@dp.callback_query_handler(text='count_call')
async def _(message: types.CallbackQuery):
    if db.check_user(message.message.from_user.id) is not None:
        db.update_logic(message.from_user.id, f'call:{db.get_logic(message.from_user.id)}')
        await bot.delete_message(chat_id=chat_admins, message_id=message.message.message_id)
        await message.message.answer('Введите кол-во звонков')
    else:
        await message.message.answer('Вас нет в базе. Пропишите /start и подайте заявку снова')


@dp.callback_query_handler(text='add_files')
async def _(message: types.CallbackQuery):
    db.update_logic(message.from_user.id, 'add_files')
    await message.message.answer('Введите номер АТС и название шаблона через |(Пример: 543|Надо поймать эту суку)',
                                 reply_markup=keyboard_back)


@dp.message_handler()
async def _(message: types.CallbackQuery):
    if db.get_logic(message.from_user.id) == 'registr':
        # await bot.send_message(-1001606427335, 'Пользователь: ' + str(message.from_user.id) + '|@' + str(
        await bot.send_message(chat_admins, 'Пользователь: ' + str(message.from_user.id) + '|@' + str(
            message.from_user.username) + '\nТекст: ' + message.text, reply_markup=keyboard_anket(message.from_user.id))
        db.update_logic(message.from_user.id, '')
        await message.reply('Отправил вашу заявку админам, после рассмотрения вам придет ответ!')
    elif 'days' in db.get_logic(message.from_user.id):
        uid = int(db.get_logic(message.from_user.id).split(':')[1])
        db.update_date_subs(uid, int(message.text))
        db.update_logic(message.from_user.id, '')
        await bot.send_message(uid, f'Вам выдан доступ на {message.text} дней', reply_markup=keyboard_menu(uid))
        await message.reply('Выдал подписку!')
    elif 'call' in db.get_logic(message.from_user.id):
        uid = int(db.get_logic(message.from_user.id).split(':')[1])
        db.update_count_call(uid, int(message.text))
        db.update_logic(message.from_user.id, '')
        await bot.send_message(uid, f'Вам выдан доступ на {message.text} звонков', reply_markup=keyboard_menu(uid))
        await message.reply('Выдал подписку!')
    elif db.get_logic(message.from_user.id) == 'add_subs':
        db.update_logic(message.from_user.id, f'{message.text}')
        await message.reply('Выберите тип подписки', reply_markup=keyboard_subs)
    elif db.get_logic(message.from_user.id) == 'del_subs':
        db.update_logic(message.from_user.id, '')
        db.update_date_subs(int(message.text))
        db.update_count_call(int(message.text), 0)
        await message.reply('Удалил подписку у пользователя!')
    elif db.get_logic(message.from_user.id) == 'phone_number':
        if datetime.datetime.now() < db.get_date_subs(message.from_user.id) or db.get_count_call(
                message.from_user.id) > 0:
            db.update_logic(message.from_user.id, 'file')
            db.update_phone_number(message.from_user.id, format_numbers(message.text))
            await message.reply('Выберите шаблон', reply_markup=keyboard_files())
        else:
            await message.reply('У вас нет доступа!', reply_markup=keyboard_registration)
    elif db.get_logic(message.from_user.id) == 'add_files':
        number = message.text.split('|')[0]
        name = message.text.split('|')[1]
        db.add_file(number, name)
        await message.answer('Успешно!')


@dp.callback_query_handler()
async def _(message: types.CallbackQuery):
    if 'success' in message.data:
        user_id = message.data.split(':')[1]
        db.update_logic(message.from_user.id, f'{user_id}')
        await bot.delete_message(chat_id=chat_admins, message_id=message.message.message_id)
        await message.message.answer('Выберите тип подписки', reply_markup=keyboard_subs)
    elif 'fail' in message.data:
        user_id = int(message.data.split(':')[1])
        await bot.send_message(user_id, 'Ваша заявку была отклонена!')
        await bot.delete_message(chat_id=chat_admins, message_id=message.message.message_id)
        await message.message.answer('Отправил отказ!')
    elif db.get_logic(message.from_user.id) == 'file':
        db.update_logic(message.from_user.id, '')
        result = api.call('/v1/request/callback/',
                          {'from': db.get_phone_number(message.from_user.id), 'to': message.data})
        if 'success' in result:
            await message.message.answer('Отправил звонок!')
            await asyncio.sleep(90)
            start = datetime.datetime.now() - datetime.timedelta(minutes=1, seconds=30)
            statisctics = ast.literal_eval(
                api.call('/v1/statistics/', {'call_type': 'out', 'start': start.strftime('%Y-%m-%d %H:%M:%S')}))
            print(statisctics)
            for call in statisctics['stats']:
                if str(db.get_phone_number(message.from_user.id))[1:] in str(call['to'])[1:]:
                    if call['disposition'] == 'answered':
                        db.update_count_call(message.from_user.id, -1)
                        generate_user_stats(message.from_user.id, message.from_user.username)

                        await message.message.answer('Успешно!', reply_markup=keyboard_menu(message.from_user.id))
                        db.update_phone_number(message.from_user.id, '')
                        break
                    else:
                        db.update_phone_number(message.from_user.id, '')
                        await message.message.answer('Результат: ' + str(errors[call['disposition']]),
                                                     reply_markup=keyboard_menu(
                                                         message.from_user.id))
                        break
        else:
            db.update_phone_number(message.from_user.id, '')
            await message.message.answer('Ошибка!Попробуйте позже', reply_markup=keyboard_menu(message.from_user.id))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
