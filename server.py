from linebot import simple_bot, reply

SB = simple_bot()


@SB.webhook
def webhook():
	pass


@SB.regex(r'^foo\d+$')
def foo():
	msg = {
		'type': 'text',
		'text': 'foo!!'
	}
	return msg


@SB.keywds(['bar', 'rab'])
def bar():
	msg = {
		'type': 'text',
		'text': 'abr!!'
	}
	return msg
