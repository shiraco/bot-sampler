# coding: utf-8

import json
import os
from logging import DEBUG, StreamHandler, getLogger

import falcon

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# logger
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_DEFAULT_TO_USER = os.environ.get('LINE_DEFAULT_TO_USER', '')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
# parser = WebhookParser(LINE_CHANNEL_SECRET)


class PushResource(object):

    def on_get(self, req, resp):

        to = req.get_param('to', default=LINE_DEFAULT_TO_USER)
        text = req.get_param('text', default='Hello World!')

        logger.debug('to user: {}'.format(to))

        try:
            line_bot_api.push_message(to, TextSendMessage(text=text))

        except LineBotApiError:
            raise falcon.HTTP_INTERNAL_SERVER_ERROR('LINE bot api error')

        resp.body = json.dumps('OK')


class WebhookResource(object):

    def on_post(self, req, resp):

        signature = req.get_header('X-Line-Signature')
        body = req.stream.read()

        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        body = body.decode('utf-8')
        logger.debug('receive_params: {}'.format(json.loads(body)))

        # handle webhook body
        try:
            handler.handle(body, signature)

        except InvalidSignatureError:
            raise falcon.HTTPBadRequest('Invalid signature error.')

        resp.body = json.dumps('OK')


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    logger.debug('event: {}'.format(event))

    user_utt = event.message.text
    sys_utt = user_utt

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=sys_utt))


api = falcon.API()
api.add_route('/webhook', WebhookResource())
api.add_route('/push', PushResource())
