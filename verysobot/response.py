class Response:
    """Generic response class with basic text/embed/attachment processing."""

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
                text = f"{msg.content}\nUrl from embed: {embed_url}"
            else:
                text = "Embed, idk"

        if msg.attachments:
            attachment = msg.attachments[0]

        return cls(text, attachment)
