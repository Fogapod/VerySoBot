class Bot:
    """Base bot class, not very useful yet."""

    def __init__(self, dbot):
        self.dbot = dbot

    def make_command(self, body):
        raise NotImplementedError
