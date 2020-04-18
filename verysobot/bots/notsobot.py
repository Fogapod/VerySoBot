from verysobot.bot import Bot
from verysobot.command import Command


class NotSoCommand(Command):
    BOT_ID = 439205512425504771
    PREFIX = "."
    EDITING_CMDS = {"ping"}
    PRE_RESPONSES = {"ok, processing"}


class NotSoBot(Bot):
    def make_command(self, body):
        return NotSoCommand(body, self.dbot)
