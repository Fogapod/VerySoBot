# TODO: logging!!!!!
# TODO: notsochallenge protection

import os
import time
import asyncio

import discord

import pykeybasebot.types.chat1 as chat1
from pykeybasebot import Bot as KBBot

from verysobot.bots.notsobot import NotSoBot
from verysobot.bots.kiwibot import KiwiBot


BOT_MAP = {
    (".", "@verysobot"): NotSoBot,
    "+": KiwiBot,
}

CHANNEL_ID = 560593330270896129

queue = asyncio.Queue()


class Handler:
    async def __call__(self, bot, event):
        if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
            return

        text = event.msg.content.text.body
        lower_text = text.lower()
        for prefix, bot in BOT_MAP.items():
            if lower_text.startswith(prefix):
                command = bot.make_command(text[len(prefix):])
                break
        else:
            return

        if not command.valid():
            return

        await queue.put((command, event.msg.conv_id))


async def forwarder(dbot, kbbot):
    while True:
        command, channel = await queue.get()
        await command.deliver(CHANNEL_ID)
        response = await command.wait_response()
  
        if response.attachment:
            # bad
            filename = f"/tmp/{round(time.time())}"

            await response.attachment.save(filename)
            await kbbot.chat.attach(channel, filename, response.text)

            os.remove(filename)
        else:
            await kbbot.chat.send(channel, response.text)


def init_bots(dbot):
    global BOT_MAP

    updated_bot_map = {}

    for prefix, bot_cls in BOT_MAP.items():
        aliases = []

        if isinstance(prefix, tuple):
            aliases.extend(prefix)
        else:
            aliases.append(prefix)

        bot = bot_cls(dbot)
        for alias in aliases:
            updated_bot_map[alias] = bot

    BOT_MAP = updated_bot_map


if __name__ == "__main__":
    dbot = discord.Client()
    kbbot = KBBot(handler=Handler())

    init_bots(dbot)

    loop = asyncio.get_event_loop()

    loop.create_task(dbot.start(os.environ["DISCORD_TOKEN"], bot=False))
    loop.create_task(kbbot.start({}))
    loop.create_task(forwarder(dbot, kbbot))

    loop.run_forever()
