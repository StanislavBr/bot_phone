import datetime
import time
from sqlighter import SQLighter
import requests

Base = SQLighter('db.db')


def get_account_datas():
    with open('active_account.txt', 'r') as file:
        api_data = file.read()

    key = api_data.split('|')[0]
    secret = api_data.split('|')[1]
    return key, secret


def get_current_date():
    now = datetime.datetime.now()
    current_date = str(
        time.mktime(
            datetime.datetime.strptime(f"{now.day}/{now.month}/{now.year}", "%d/%m/%Y").timetuple()
        )
    ).split('.')[0]
    return current_date


def generate_user_stats(chat_id, username):
    if Base.get_stats_data(chat_id=chat_id) is None:
        Base.insert_user_stats(chat_id=chat_id, count=1, date_time=str(get_current_date()), username=username)
    else:
        if int(Base.get_stats_data(chat_id=chat_id)[2]) < int(get_current_date()):
            Base.delete_from_stats(chat_id=chat_id)
            Base.insert_user_stats(chat_id=chat_id, count=1, date_time=str(get_current_date()))
        else:
            user_data = Base.get_stats_data(chat_id=chat_id)
            Base.update_stats_value(chat_id=chat_id, column='count_call', value=int(user_data[1]) + 1)


def format_numbers(phone_number: str) -> str:
    try:
        return '8{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}'.format(*[i for i in phone_number if i.isdigit()][1:])
    except:
        return '89999999999'


def send_call_log(user_id, text):
    with open('botwork_token.txt', 'r') as f:
        token = f.read()
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={user_id}&text={text}&parse_mode=html"
    requests.get(url=url)