from linebot import simple_bot

SB = simple_bot()


@SB.webhook
def webhook():
	return 'Hi'

SB.init_reply()
