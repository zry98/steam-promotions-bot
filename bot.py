#!/usr/bin/env python
from os import environ
import logging
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from telegram.utils import request
from get_promotions import get_freebies_list

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN: str = environ['BOT_TOKEN']
CHANNEL_ID: str = environ['CHANNEL_ID']
ADMIN_ID: int = int(environ['ADMIN_ID'])


def start(update, ctx):
    update.message.reply_text('Hi! This is a Steam promotions notify bot.')


def error(update, ctx):
    logger.warning('Update "%s" caused error "%s"', update, ctx.error)


def plain_text(text: str) -> str:
    return text \
        .replace('<', '&lt;') \
        .replace('>', '&gt;') \
        .replace('&', '&amp;')


def get_freebies(update, ctx):
    freebies = get_freebies_list()
    if isinstance(freebies, str):
        logger.warning(freebies)  # log error
        update.message.reply_text('Server error', disable_notification=True)
        return

    for freebie in freebies:
        line = '<a href="https://store.steampowered.com/app/{}">{}</a>' \
            .format(freebie['appid'], plain_text(freebie['name']))

        if 'is_dlc' in freebie and freebie['is_dlc']:
            line += '\n\n(This is a DLC of <a href="https://store.steampowered.com/app/{}">{}</a>)' \
                .format(freebie['fullgame_appid'], plain_text(freebie['fullgame_name']))

        update.message.reply_html(line, disable_notification=True)


def post_notify_to_channel(update, ctx):
    if update.message.from_user.id == ADMIN_ID:
        freebies = get_freebies_list()
        if isinstance(freebies, str):
            logger.warning(freebies)  # log API error
            update.message.reply_text('Server error', disable_notification=True)
            return

        for freebie in freebies:
            line = '<a href="https://store.steampowered.com/app/{}">{}</a>' \
                .format(freebie['appid'], plain_text(freebie['name']))

            if 'is_dlc' in freebie and freebie['is_dlc']:
                line += '\n\n(This is a DLC of <a href="https://store.steampowered.com/app/{}">{}</a>)' \
                    .format(freebie['fullgame_appid'], plain_text(freebie['fullgame_name']))

            global BOT
            BOT.send_message(chat_id='@steam_promotions', text=line, parse_mode='HTML')

        update.message.reply_html('OK')


def main():
    global BOT
    BOT = Bot(BOT_TOKEN, request=request.Request(con_pool_size=8))
    updater = Updater(bot=BOT, use_context=True, workers=4)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('get_freebies', get_freebies))
    dp.add_handler(CommandHandler('post_notify_on_channel', post_notify_to_channel))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
