from verysobot.response import Response


# timeout for waiting bot responses
TIMEOUT = 10


class Command:
    """Basic command class. Shoud be subclassed."""

    # id of discord bot
    BOT_ID = 0

    # prefix of discord bot
    PREFIX = ""

    # bot edits some responses with actual results, these should be waited from
    # message_update event
    EDITING_CMDS = set()

    # some commands send message before actual response, these messages should be
    # ignored
    PRE_RESPONSES = set()

    def __init__(self, body, dbot):
        self._body = body
        self._command = self._get_command(self._body)

        self._dbot = dbot

        self._channel_id = None

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
        return self._command in self.EDITING_CMDS

    def _prepare(self):
        return f"{self.PREFIX}{self._body}"

    async def deliver(self, channel_id):
        await self._dbot.http.send_message(channel_id, self._prepare())

        self._channel_id = channel_id

    async def wait_response(self, response_cls=Response, timeout=TIMEOUT):
        if self._channel_id is None:
            raise RuntimeError("Command not delivered")

        def _location_check(msg):
            return msg.channel.id == self._channel_id and msg.author.id == self.BOT_ID

        def check(msg):
            return _location_check(msg) and msg.content not in self.PRE_RESPONSES

        def editing_check(old, new):
            return _location_check(new)

        try:
            if self.editing:
                _, msg = await self._dbot.wait_for(
                    "message_edit",
                    timeout=timeout,
                    check=editing_check
                )
            else:
                msg = await self._dbot.wait_for(
                    "message",
                    timeout=timeout,
                    check=check
                )
        except asyncio.TimeoutError:
            return response_cls("Timed out", None)

        return response_cls.from_message(msg)

    def __str__(self):
        return self._body
