#!/usr/bin/env python
from os import environ
import logging
from telegram import Bot, ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.utils import request
from get_promotions import get_freebies_list

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN: str = environ['BOT_TOKEN']
CHANNEL_ID: str = environ['CHANNEL_ID']
ADMIN_ID: int = int(environ['ADMIN_ID'])

BOT: Bot


def start(update, ctx):
    update.message.reply_text('Hi! This is a Steam promotions news bot.\n'
                              'Use /get_freebies to get a list of FREE keepable promotions.')


def error(update, ctx):
    logger.warning('Update "%s" caused error "%s"', update, ctx.error)


def plain_text(text: str) -> str:
    return text \
        .replace('<', '&lt;') \
        .replace('>', '&gt;') \
        .replace('&', '&amp;')


def build_freebies_message() -> str:
    freebies = get_freebies_list()
    if isinstance(freebies, str):
        logger.warning(freebies)  # log error
        return 'Server error'

    msg = 'Currently live free keepable promotions\n\n'
    for freebie in freebies:
        line = '<a href="https://store.steampowered.com/app/{}">{}</a>' \
            .format(freebie['appid'], plain_text(freebie['name']))

        if 'is_dlc' in freebie and freebie['is_dlc']:
            line += '  (a DLC of <a href="https://store.steampowered.com/app/{}">{}</a>)' \
                .format(freebie['fullgame_appid'], plain_text(freebie['fullgame_name']))

        msg += line + '\n\n'

    return msg


def get_freebies(update, ctx):
    msg = build_freebies_message()

    update.message.reply_html(msg, disable_notification=True, disable_web_page_preview=True)


def post_notify_onto_channel(update, ctx):
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text('Unauthorized')
        return

    msg = build_freebies_message()
    if msg == 'Server error':
        update.message.reply_text('Server error')
        return

    global BOT
    BOT.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode=ParseMode.HTML,
                     disable_notification=True, disable_web_page_preview=True)

    update.message.reply_text('OK')


def main():
    global BOT
    BOT = Bot(BOT_TOKEN, request=request.Request(con_pool_size=8))
    updater = Updater(bot=BOT, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('get_freebies', get_freebies))
    dp.add_handler(CommandHandler('post_notify', post_notify_onto_channel))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
