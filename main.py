# KEYBASE_USERNAME and KEYBASE_PAPERKEY env vars are required to run keybase bot
# DISCORD_TOKEN env var is required to run discord bot

# TODO: running commands on a private server in multiple channels in parallel

import os
import time
import asyncio

import discord

import pykeybasebot.types.chat1 as chat1
from pykeybasebot import Bot as KBBot


# prefixes for using bot in Keybase
PREFIXES = {".", "@verysobot"}

NSB_ID = 439205512425504771
CHANNEL_ID = 560593330270896129


# some commands send message before actual response, these messages should be ignored
PRE_RESPONSES = {
    "ok, processing",
}

# bot edits some responses with actual results, these should be waited from 
# message_update event
EDITING_CMDS = {
    "ping",
}

# timeout for waiting NotSoBot response
TIMEOUT = 10

lock = asyncio.Lock()
queue = asyncio.Queue()

bot = discord.Client()


class NotSoCommand:
    def __init__(self, text, prefix):
        self._body = self._strip_prefix(text, prefix)
        self._command = self._get_command(self._body)

    @staticmethod
    def _strip_prefix(text, prefix):
        return text[len(prefix):]

    @staticmethod
    def _get_command(body):
        args = body.split(maxsplit=1)

        return args[0] if args else ""

    def valid(self):
        return self._command != ""

    @property
    def editing(self):
        return self._command in EDITING_CMDS

    def _prepare(self):
        return f".{self._body}"

    async def deliver(self):
        await bot.http.send_message(CHANNEL_ID, self._prepare())

    async def wait_response(self, timeout=TIMEOUT):
        def _location_check(msg):
            return msg.channel.id == CHANNEL_ID and msg.author.id == NSB_ID

        def check(msg):
            return _location_check(msg) and msg.content not in PRE_RESPONSES

        def editing_check(old, new):
            return _location_check(new)

        try:
            if self.editing:
                _, msg = await bot.wait_for(
                    "message_edit",
                    timeout=timeout,
                    check=editing_check
                )
            else:
                msg = await bot.wait_for("message", timeout=timeout, check=check)
        except asyncio.TimeoutError:
            return NotSoResponse("Timed out", None)

        return NotSoResponse.from_message(msg)

    def __str__(self):
        return self._body


class NotSoResponse:
    def __init__(self, text, attachment):
        self.text = text
        self.attachment = attachment

    @classmethod
    def from_message(cls, msg):
        text = msg.content
        attachment = None

        if msg.embeds:
            embed = msg.embeds[0]
            embed_url = None

            if embed.image:
                embed_url = embed.image.url
            elif embed.thumbnail:
                embed_url = embed.thumbnail.url

            if embed_url:
                text = f"{msg.content}\n{embed_url}"
            else:
                text = "Embed, idk"

        if msg.attachments:
            attachment = msg.attachments[0]

        return cls(text, attachment)


class Handler:
    async def __call__(self, bot, event):
        if event.msg.content.type_name != chat1.MessageTypeStrings.TEXT.value:
            return

        text = event.msg.content.text.body
        lower_text = text.lower()
        for prefix in PREFIXES:
            if lower_text.startswith(prefix):
                command = NotSoCommand(text, prefix)
                break
        else:
            return

        if not command.valid():
            return

        await queue.put((command, event.msg.conv_id))


async def forwarder(kbbot):
    while True:
        command, channel = await queue.get()
        async with lock:
            await command.deliver()
            response = await command.wait_response()
  
            if response.attachment:
                # bad
                filename = f"/tmp/{round(time.time())}"

                await response.attachment.save(filename)
                await kbbot.chat.attach(channel, filename, response.text)

                os.remove(filename)
            else:
                await kbbot.chat.send(channel, response.text)

        
if __name__ == "__main__":
    kbbot = KBBot(handler=Handler())

    loop = asyncio.get_event_loop()

    loop.create_task(bot.start(os.environ["DISCORD_TOKEN"], bot=False))
    loop.create_task(kbbot.start({}))
    loop.create_task(forwarder(kbbot))

    loop.run_forever()
