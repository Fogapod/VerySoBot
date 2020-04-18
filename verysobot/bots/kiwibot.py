from verysobot.bot import Bot
from verysobot.command import Command


class KiwiCommand(Command):
    BOT_ID = 394793577160376320
    PREFIX = "+"
    EDITING_CMDS = {"ping"}


class KiwiBot(Bot):
    def make_command(self, body):
        return KiwiCommand(body, self.dbot)
