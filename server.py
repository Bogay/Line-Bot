import random

from linebot import simple_bot

SB = simple_bot()


@SB.webhook
def webhook():
    pass

@SB.regex(r'.*@?特世 *謝謝.*')
def anytime():
    msg = {
        'type': 'text',
        'text': '我拿槍了嗎' if random.random() < 0.05 else '不客氣' 
    }
    return msg

