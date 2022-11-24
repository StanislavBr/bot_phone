from aiogram import types
from sqlighter import SQLighter
import os

# admin_id = [2097372864]
admin_id = [2128716518, 1532786700, 2097372864, 1440388151, 5048314108, 1765076992, 2119114154, 808219163, 1859007058]
db = SQLighter('db.db')


def admin_service_key():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Добавить новый аккаунт', callback_data='add_account'),
                 types.InlineKeyboardButton('Просмотреть все аккаунты', callback_data='show_account'))
    return keyboard


def cancel_acc():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Отмена', callback_data='cancelling'))
    return keyboard


def accounts_keyboard():
    keyboards = types.InlineKeyboardMarkup()
    with open('active_account.txt', 'r') as file:
        active = file.read()
    for value in db.get_all_accounts():
        status = '🟢Активен' if str(value[0]) == str(active.split('|')[0]) else '🔚Активировать'
        data = '*' if str(value[0]) == str(active.split('|')[0]) else 'set_account'
        print(value[0], data, active)
        keyboards.add(
            types.InlineKeyboardButton(
                text=f'key: {str(value[0])[:7]} | secret: {str(value[1])[:5]}',
                # callback_data=f'delete_acc|{value[0]}|{value[1]}'
                callback_data='/*'
            ), types.InlineKeyboardButton(
                text=status,
                callback_data=f'{data}|{value[0]}|{value[1]}'
            )
        )
        keyboards.add(
            types.InlineKeyboardButton(
                text='Удалить',
                callback_data=f'delete_acc|{value[0]}|{value[1]}'
            )
        )
    return keyboards


def keyboard_menu(uid):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Позвонить', callback_data='call'),
                 types.InlineKeyboardButton('Мой аккаунт', callback_data='profile'))
    if uid in admin_id:
        keyboard.add(types.InlineKeyboardButton('Добавить подписку', callback_data='add_subs'),
                     types.InlineKeyboardButton('Убрать подписку', callback_data='del_subs'))
        keyboard.add(types.InlineKeyboardButton('Добавить шаблон', callback_data='add_files'))
    return keyboard


keyboard_registration = types.InlineKeyboardMarkup()
keyboard_registration.add(types.InlineKeyboardButton('Регистрация', callback_data='registr'))


def keyboard_anket(user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Принять', callback_data='success:' + str(user_id)),
                 types.InlineKeyboardButton('Отклонить', callback_data='fail:' + str(user_id)))
    return keyboard


def keyboard_files():
    keyboard = types.InlineKeyboardMarkup()
    for file in db.get_file():
        keyboard.add(types.InlineKeyboardButton(file[1], callback_data=file[0]))
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='back'))
    return keyboard


keyboard_subs = types.InlineKeyboardMarkup()
keyboard_subs.add(types.InlineKeyboardButton('По дням', callback_data='days'),
                  types.InlineKeyboardButton('По звонкам', callback_data='count_call'))

keyboard_back = types.InlineKeyboardMarkup()
keyboard_back.add(types.InlineKeyboardButton('Назад', callback_data='back'))
