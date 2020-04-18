# this is temporary solution until command invocation moved from notsoserver

import re


MAX_SAFE_MENTIONS = 5

ID_EXPR = "\d{17,19}"
USER_MENTION_EXPR = f'<@!?({ID_EXPR})>'

USER_MENTION_REGEX = re.compile(USER_MENTION_EXPR)


def antinotsochallenge(text):
    mentions = USER_MENTION_REGEX.findall(text)
    if len(mentions) > MAX_SAFE_MENTIONS:
        return ".t say Notsochallenge failed"

    return text
