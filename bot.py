#!/usr/bin/env python3.8

import os
import io
import telebot
import sqlite3 as lite
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
from config import TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DBFILE = os.path.join(SCRIPT_DIR, "plotbot.db")

bot = telebot.TeleBot(TOKEN)
con = lite.connect(DBFILE, detect_types=lite.PARSE_DECLTYPES)
with con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS log(user_id TXT, date TIMESTAMP, num INT)")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Send me a number and i will reply with a graph of all the received numbers.")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if not message.text.isnumeric():
        return bot.reply_to(message, 'Please send a positive integer number')
    num = int(message.text)
    user = message.from_user
    logging.info('User %s (%s): %s', user.id, user.username, num)
    store_number(user_id=user.id, num=num)
    photo = generate_plot(user.id)
    bot.send_photo(user.id, photo)
    photo.close()


def store_number(user_id, num):
    con = lite.connect(DBFILE, detect_types=lite.PARSE_DECLTYPES)
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO log (user_id, date, num) VALUES(?, ?, ?);", (user_id, datetime.datetime.now(), num))


def generate_plot(user_id):
    con = lite.connect(DBFILE, detect_types=lite.PARSE_DECLTYPES)
    with con:
        cur = con.cursor()
        res = cur.execute("SELECT date, num FROM log WHERE user_id == ? ORDER BY date;", (user_id,))
    x, y = zip(*res)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.plot(x, y, 'b')
    ax.set_xlabel('Date')
    plt.xticks(rotation=20)
    # plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf


bot.infinity_polling()
