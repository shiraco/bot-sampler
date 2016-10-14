import json
import os
from logging import DEBUG, StreamHandler, getLogger

import requests

import falcon

# logger
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

REPLY_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')


class WebhookResource(object):
    header = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {}'.format(LINE_CHANNEL_ACCESS_TOKEN)
    }

    def on_post(self, req, resp):

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        receive_params = json.loads(body.decode('utf-8'))
        logger.debug('receive_params: {}'.format(receive_params))

        for event in receive_params['events']:

            logger.debug('event: {}'.format(event))

            if event['type'] == 'message':
                user_utt = event['message']['text']
                sys_utt = user_utt

                send_content = {
                    'replyToken': event['replyToken'],
                    'messages': [
                        {
                            'type': 'text',
                            'text': sys_utt
                        }

                    ]
                }
                send_content = json.dumps(send_content)
                logger.debug('send_content: {}'.format(send_content))

                res = requests.post(REPLY_ENDPOINT, data=send_content, headers=self.header)
                logger.debug('res: {} {}'.format(res.status_code, res.reason))

                resp.body = json.dumps('OK')


api = falcon.API()
api.add_route('/webhook', WebhookResource())
