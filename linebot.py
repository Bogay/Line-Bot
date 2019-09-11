from bottle import Bottle, request, HTTPResponse
from functools import wraps

import base64
import hashlib
import hmac
import json
import requests
import os
import configparser

channel_secret = os.environ.get('channel_secret')
access_token = os.environ.get('access_token')

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {{{access_token}}}'
}

REPLY_URL = 'https://api.line.me/v2/bot/message/reply'


class simple_bot(Bottle):
    def __init__(self, reply_cfg='reply.cfg'):
        Bottle.__init__(self)
        self.reply_cfg = reply_cfg


    def init_reply(self):
        reply_list = configparser.ConfigParser()
        reply_list.read(self.reply_cfg)
        for key in reply_list.keys():
            if key in globals():
                raise ValueError(f'Name \'{key}\' has been used.')
            r = reply_list[key]
            rep = r.get('regex')
            kwd = r.get('keywd')
            if rep:
                globals()[key] = self.regex(rep)(reply(r))
            elif kwd:
                kwds_list = kwd.split('|')
                globals()[key] = self.keywds(kwds_list)(reply(r))
        for r in self.routes:
            print(r)


    def regex(self, rep):

        return self.post(f'/regex/<:re:{rep}>')


    def keywds(self, kwds_list):
        rep = f'.*({"|".join(kwds_list)}).*'

        return self.regex(rep)

    def webhook(self, func):
        def webhook_func(gunc):
            @wraps(gunc)
            @validate_signature
            def wrapper(*args, **kwds):
                ret = gunc(*args, **kwds)
                body = json.loads(request.body.read().decode('utf8')).get('events')
                if body and body[0].get('message', {}).get('type') == 'text':
                    token = body[0].get('replyToken') if body else None
                    text = body[0]['message']['text']
                    data = {'token': token}
                    requests.post(f'https://localhost/regex/{text}', data=data)

                return ret
            return wrapper
        return self.post('/webhook')(webhook_func(func))


def run(bot=None, **kwds):
    if bot:
        bot.init_reply()
        bot.run(**kwds)


def validate_signature(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        body = request.body.read()
        hash_value = hmac.new(channel_secret.encode('utf-8'), body, hashlib.sha256).digest()
        signature = base64.b64encode(hash_value)
        X_Line_Signature = request.headers.get('X-Line-Signature', '').encode('utf-8')
        if not (X_Line_Signature and signature == X_Line_Signature):
            return HTTPResponse(status=403)
        return func(*args, **kwds)

    return wrapper


def reply(msg):
    def reply_func():
        token = request.forms.get('token')
        if token:
            data = {
                'replyToken': token,
                'messages': [msg]
            }
            requests.post(REPLY_URL, headers=HEADERS, json=data)

    return reply_func
        