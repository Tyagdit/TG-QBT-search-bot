import requests
import pprint
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import (Updater, MessageHandler, Filters, CommandHandler, InlineQueryHandler, ConversationHandler, RegexHandler, CallbackQueryHandler)
import logging
import qbittorrentapi
import time

class qbt_search():
        
    def __init__(self, search_term):

        self.qbt_client = qbittorrentapi.Client(host='', username='', password='')

        try:
            self.qbt_client.auth_log_in()
        except qbittorrentapi.LoginFailed as e:
            print(e)
        
        self.search_job = self.qbt_client.search_start(pattern=search_term, category='all', plugins='all')
        
        while (self.search_job.status()[0].status != 'Stopped'):
            time.sleep(.1)

        self.search_result = self.qbt_client.search_results(id=self.search_job.id, limit = 3, offset = 1)
        
        self.magnet_list = [result.fileUrl for result in self.search_result.results] 

#Bot functions
def start(bot, update):
    bot.send_message('Hi, this is a bot to search for torrents. Use /search <name>.')

def search(bot, update):

    msg = update.message
    chat_id = msg.chat_id

    text = msg.text.split(' ')
    search = " "
    search = search.join(text[1:])
    print(search)

    bot.send_message(chat_id=chat_id, text="Fetching results...")

    search_obj = qbt_search(search)

    title = ''

    for result in search_obj.search_result.results:
        title = title + f"Name: {result.fileName}\nSeeders: {result.nbSeeders}\nSize: {result.fileSize}\n\n"

    keyboard = [[InlineKeyboardButton(text="Magnet 1", callback_data=search+'0')],
                [InlineKeyboardButton(text="Magnet 2", callback_data=search+'1')],
                [InlineKeyboardButton(text="Magnet 3", callback_data=search+'2')]]

    kb_markup = InlineKeyboardMarkup(keyboard)
    try:
        bot.send_message(chat_id=chat_id, text=title, reply_markup=kb_markup)
    except: bot.send_message(chat_id=chat_id, text="No results found")

def button(bot, update):
    
    query = update.callback_query
    query.answer()
    
    query.bot.send_message(chat_id=query.message.chat_id, text="sending magnet")

    search_obj = qbt_search(query.data[:-1])
    index = int(query.data[-1])
    
    query.bot.send_message(chat_id=query.message.chat_id, text=search_obj.magnet_list[index])

def main():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    updater = Updater(token="")

    dispatcher = updater.dispatcher

    search_handler = CommandHandler('search', search)
    dispatcher.add_handler(CallbackQueryHandler(button))

    dispatcher.add_handler(search_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
