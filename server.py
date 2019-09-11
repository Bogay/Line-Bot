from linebot import simple_bot, run

SB = simple_bot()


@SB.webhook
def webhook():
	return 'Hi'


if __name__ == '__main__':
    run(bot=SB)
