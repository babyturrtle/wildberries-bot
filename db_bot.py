#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A Telegram bot for extracting data from Wildberries website.
"""

import logging

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from bs4 import BeautifulSoup
import requests

import sqlite3
from sqlite3 import Error

TOKEN = "2108948340:AAE0aozUsv1j1AM8bP4JCITFQv-tDl0Ru5s"
database = "products_sqlite.db"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def create_connection(db_file):
    """ Creates a database connection to an SQLite database. """

    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_product(conn, article, title):
    """ Insert the product data into SQLite database. """

    sql = ''' INSERT INTO product (article, title) VALUES (?, ?)
    ON CONFLICT (article) DO UPDATE SET title = (?) '''

    cur = conn.cursor()
    cur.execute(sql, (article, title, title))
    conn.commit()


def create_brand(conn, brand):
    """ Insert the brand data into SQLite database. """

    sql = ''' INSERT OR IGNORE INTO brand (name) VALUES (?)'''

    cur = conn.cursor()
    cur.execute(sql, (brand,))
    conn.commit()

    return cur.lastrowid


def update_product(conn, article, brand_id):
    """ Update the relationship in product table in SQLite database. """

    sql = ''' INSERT INTO product(article, brand_id) VALUES (?, ?) 
    ON CONFLICT(article) DO UPDATE SET brand_id = (?) '''

    cur = conn.cursor()
    cur.execute(sql, (article, brand_id, brand_id))
    conn.commit()


def start(update, context):
    """Sends explanation on how to use the bot."""

    update.message.reply_text('Привет!👋 '
                              '\nЯ бот, который соберёт для тебя самую важную информацию на сайте *Wildberries*.\n'
                              '\nЧтобы узнать бренд товара, введи `/get_brand <артикул товара>`.'
                              '\nЧтобы узнать наименование товара, введи `/get_title <артикул товара>`.',
                              parse_mode=telegram.ParseMode.MARKDOWN)


def get_brand(update, context):
    """ Gets brand name by item's article. """

    article = context.args[0]
    url = 'https://www.wildberries.ru/catalog/' + article + '/detail.aspx'
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        brand = soup.find('meta', {"itemprop": "brand"}).get("content")
        update.message.reply_text(brand)
        conn = create_connection(database)
        with conn:
            brand_id = create_brand(conn, brand)
            update_product(conn, article, brand_id)
    except:
        update.message.reply_text("Товар не найден.")


def get_title(update, context):
    """ Gets item's title by its article. """

    article = context.args[0]
    url = 'https://www.wildberries.ru/catalog/' + article + '/detail.aspx'
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        title = soup.find('meta', {"itemprop": "name"}).get("content")
        update.message.reply_text(title)

        conn = create_connection(database)
        with conn:
            create_product(conn, article, title)
    except:
        update.message.reply_text("Товар не найден.")


def unknown(update, context):
    """ Replies to an unknown command. """

    context.bot.send_message(chat_id=update.effective_chat.id, text="Хм... Я не знаю такой команды.")


def main():
    """ Starts the bot. """

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get_brand", get_brand))
    dp.add_handler(CommandHandler("get_title", get_title))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
