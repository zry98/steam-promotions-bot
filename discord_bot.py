from os import environ
from get_promotions import get_freebies_list
import discord

BOT_TOKEN: str = environ['BOT_TOKEN']


async def get_freebies(message):
    freebies = get_freebies_list()
    if isinstance(freebies, str):
        await message.channel.send('Server error')

    msg = ''
    for freebie in freebies:
        line = '{}\nhttps://store.steampowered.com/app/{}' \
            .format(freebie['name'], freebie['appid'])

        if 'is_dlc' in freebie and freebie['is_dlc']:
            line += '\n(This is a DLC of {} https://store.steampowered.com/app/{})' \
                .format(freebie['fullgame_name'], freebie['fullgame_appid'])

        msg += line + '\n\n'

    await message.channel.send(msg)


def main():
    bot = discord.Client()

    @bot.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(bot))

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if message.content == '/get_freebies':
            await get_freebies(message)

    bot.run(BOT_TOKEN)


if __name__ == '__main__':
    main()
