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

TOKEN = "TOKEN GOES HERE"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


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
