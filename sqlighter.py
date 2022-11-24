import sqlite3
import datetime


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
   user_id INT PRIMARY KEY,
   date_subs TEXT,
   count_call INT,
   logic TEXT,
   phone_number TEXT
   );
""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS files(
   number INT PRIMARY KEY,
   name TEXT
   );
""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS stats(
        chat_id int,
        count_call int,
        last_day TEXT,
        username TEXT
        );""")

    def user_exists(self, user_id):
        with self.connection:
            return bool(len(self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()))

    def user_add(self, user_id, date_subs=datetime.datetime.now().strftime('%Y/%m/%d/%H/%M/%S/%f'), logic='',
                 phone_number='', count_call=0):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `users` (user_id, date_subs, logic, phone_number, count_call) VALUES(?,?,?,?,?)",
                (user_id, date_subs, logic, phone_number, count_call))

    def get_date_subs(self, user_id):
        with self.connection:
            date = self.cursor.execute("SELECT `date_subs` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][
                0]
            return datetime.datetime.strptime(date, '%Y/%m/%d/%H/%M/%S/%f')

    def get_logic(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `logic` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def get_phone_number(self, user_id):
        with self.connection:
            return \
            self.cursor.execute("SELECT `phone_number` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def get_count_call(self, user_id):
        with self.connection:
            return \
            self.cursor.execute("SELECT `count_call` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]

    def update_date_subs(self, user_id, date_subs=datetime.datetime.now().strftime('%Y/%m/%d/%H/%M/%S/%f')):
        with self.connection:
            if isinstance(date_subs, int):
                date_subs = datetime.datetime.now() + datetime.timedelta(days=int(date_subs))
                date_subs = date_subs.strftime('%Y/%m/%d/%H/%M/%S/%f')
            return self.cursor.execute("UPDATE `users` SET `date_subs` = ? WHERE `user_id` = ?", (date_subs, user_id))

    def update_logic(self, user_id, logic):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `logic` = ? WHERE `user_id` = ?", (logic, user_id))

    def update_phone_number(self, user_id, phone_number):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `phone_number` = ? WHERE `user_id` = ?",
                                       (phone_number, user_id))

    def update_count_call(self, user_id, call):
        with self.connection:
            if call == 0:
                return self.cursor.execute("UPDATE `users` SET `count_call` = ? WHERE `user_id` = ?", (call, user_id))
            else:
                count_call = \
                self.cursor.execute("SELECT `count_call` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()[0][0]
                count_call += call
                return self.cursor.execute("UPDATE `users` SET `count_call` = ? WHERE `user_id` = ?",
                                           (count_call, user_id))

    def add_file(self, number, name):
        with self.connection:
            return self.cursor.execute("INSERT INTO `files` (number, name) VALUES (?,?)", (int(number), name))

    def get_file(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `files`").fetchall()

    def write_account(self, key, secret):
        with self.connection:
            return self.cursor.execute('insert into `accounts` (key, secret) values (?,?)', (key, secret))

    def get_all_accounts(self):
        with self.connection:
            return self.cursor.execute('select * from `accounts`').fetchall()

    def delete_accounts(self, value):
        with self.connection:
            return self.cursor.execute('delete from `accounts` where key = ?', (value,))

    def check_user(self, chat_id):
        with self.connection:
            data = self.cursor.execute('select * from users where user_id = ?', (chat_id,)).fetchone()
            print(data)
            return data

    def insert_user_stats(self, chat_id, count, date_time, username):
        with self.connection:
            self.cursor.execute('insert into stats values (?, ?, ?, ?)', (chat_id, count, date_time, username))
            self.connection.commit()

    def get_stats_data(self, chat_id):
        with self.connection:
            self.cursor.execute('select * from stats where chat_id = ?', (chat_id,))
            return self.cursor.fetchone()

    def delete_from_stats(self, chat_id):
        with self.connection:
            self.cursor.execute('delete from stats where chat_id = ?', (chat_id,))
            self.connection.commit()

    def get_all_stats_data(self):
        with self.connection:
            self.cursor.execute('select * from stats')
            return self.cursor.fetchall()

    def update_stats_value(self, chat_id, column, value):
        with self.connection:
            self.cursor.execute(f'update stats set {column} = ? where chat_id = ?', (value, chat_id))
            self.connection.commit()

    def delete_last_stats(self, date_now):
        with self.connection:
            self.cursor.execute('delete from stats where last_day < ?', (date_now,))
            self.connection.commit()