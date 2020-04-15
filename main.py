import requests
import pprint
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import (Updater, MessageHandler, Filters, CommandHandler, InlineQueryHandler, ConversationHandler, RegexHandler, CallbackQueryHandler)
import logging
import qbittorrentapi
import time

#Bot functions
def start(bot, update):
        bot.send_message('Hi, this is a bot to search for torrents. Use /search <name>.')

def search(bot, update):

        msg = update.message
        chat_id = msg.chat_id

        text = msg.text.split(' ')
        search = text[1]
        print(search)

        qbt_client = qbittorrentapi.Client(host='192.168.1.248:8080', username='admin', password='adminadmin')

        try:
            qbt_client.auth_log_in()
        except qbittorrentapi.LoginFailed as e:
            print(e)

        search_job = qbt_client.search.start(pattern=search, category='all', plugins='all')

        while (search_job.status()[0].status != 'Stopped'):
            time.sleep(.1)

        search_result = qbt_client.search_results(id=search_job.id, limit = 3, offset = 1)

        magnet_list = []
        title = ''

        for result in search_result.results:
            i = result.fileUrl.index('&')
            title = title + f"Name: {result.fileName}\nSeeders: {result.nbSeeders}\nSize: {result.fileSize}\n\n"
            magnet_list.append(f"Magnet:\n{result.fileUrl[:i]}")
            print(magnet_list)

        keyboard = [[InlineKeyboardButton(text="Magnet 1", callback_data=magnet_list[0])],
                    [InlineKeyboardButton(text="Magnet 2", callback_data=magnet_list[1])],
                    [InlineKeyboardButton(text="Magnet 3", callback_data=magnet_list[2])]]

        kb_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text=title, reply_markup=kb_markup)

def button(bot, update):
        query = update.callback_query

        query.bot.send_message(chat_id=query.message.chat_id, text=query.data)

def main():

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        updater = Updater(token="1128514006:AAHVDTxMv_mWqnZzghzPWfGxHwiSVOKfgY8")

        dispatcher = updater.dispatcher

        search_handler = CommandHandler('search', search)

        dispatcher.add_handler(search_handler)

        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    main()
