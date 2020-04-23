import requests
import pprint
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, InlineQueryHandler, ConversationHandler, RegexHandler, CallbackQueryHandler
import logging
import qbittorrentapi
import time

#Bot functions
def start(update, context):
    context.bot.send_message("Hi, this is a bot to search for torrents. Use /search <name>.")

def search(update, context):
    
    context.chat_data.clear()

    chat_id = update.effective_chat.id
    message_info = context.bot.send_message(chat_id=chat_id, text="Fetching results...")
    context.chat_data['msg_id'] = message_info.message_id

    search = ' '.join(context.args)
    print(f"New search: {search}")
    
    #perform search 
    qbt_client = qbittorrentapi.Client(host='', username='', password='')

    try:
        qbt_client.auth_log_in()
    except qbittorrentapi.LoginFailed as err:
        print(err)
    
    search_job = qbt_client.search_start(pattern=search, category='all', plugins='all')
    
    while search_job.status()[0].status != 'Stopped':
        time.sleep(.1)

    search_result = search_job.results(limit=5, offset=1)

    context.chat_data['magnet_list'] = [result.fileUrl for result in search_result.results]

    #construct message
    title = ''
    for result in search_result.results:
        title = title + f"*Name:* _{result.fileName}_\n*Seeders:* _{result.nbSeeders}_\n*Size:* _{round(result.fileSize/(1024**3),2)} GB_\n\n"

    #Construct inline keybpoard
    kb_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='Magnet 1', callback_data=f'0'), InlineKeyboardButton(text='Magnet 2', callback_data=f'1')],
                    [InlineKeyboardButton(text='Magnet 3', callback_data=f'2'), InlineKeyboardButton(text='Magnet 4', callback_data=f'3')],
                    [InlineKeyboardButton(text='Magnet 5', callback_data=f'4')]
                ])

    search_job.delete()

    try:
        context.bot.edit_message_text(message_id = context.chat_data['msg_id'], chat_id=chat_id, text=title, reply_markup=kb_markup, parse_mode = 'markdown')
    except Exception as err: 
        context.bot.edit_message_text(message_id = context.chat_data['msg_id'], chat_id=chat_id, text="No results found")
        print(err)
    else:
        print("Search result found")

def button(update, context):
    
    query = update.callback_query
    index = int(query.data)

    query.answer()
   
    if context.chat_data['magnet_list'][index].startswith('https'):
        magnet = f"{context.chat_data['magnet_list'][index]}"
    else:
        magnet = f"```{context.chat_data['magnet_list'][index]}```"

    if query.message.message_id != context.chat_data['msg_id']:
        query.bot.edit_message_text(message_id=query.message.message_id, chat_id=query.message.chat_id, text="Search expired")
    else:
        mag_msg = query.bot.send_message(chat_id=query.message.chat_id, text="sending magnet...")
        query.bot.edit_message_text(message_id=mag_msg.message_id, chat_id=query.message.chat_id, text=magnet, parse_mode='markdown')

def main():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    updater = Updater(token="", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('search', search))

    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
