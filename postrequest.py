#!/usr/bin/env python
import httplib
import urllib
import json

SERVER = 'api.telegram.org'
with open('api-key.txt', 'r') as f:
  key = f.read().strip()
BOT = '/bot%s/' % (key)
OFFSET_FILE = 'offset.txt'

def send_request(method, data={}):
  c = httplib.HTTPSConnection(SERVER)
  params = urllib.urlencode(data)
  headers = {"Content-type": "application/x-www-form-urlencoded"}
  c.request('POST', BOT + method, params, headers)
  r = c.getresponse()
  if r.status != 200:
    raise Exception('HTTP response %s: %s' % (r.status, r.reason))
  try:
    res = r.read()
    o = json.loads(res)
    if o['ok'] is not True:
      raise Exception('Method returned failure: %s' % (o.get('result')))
    return o['result']
  except Exception, e:
    raise Exception('Error parsing response JSON: %s' % (res))


def update_offset(offset):
  x = get_offset()
  if offset > x:
   with open(OFFSET_FILE, 'w') as f:
     f.write(str(offset))

def get_offset():
  with open(OFFSET_FILE, 'r') as f:
    x = f.read()
    return int(x)

def process_messages(messages):
  for message in messages:
    process_message(message)

def send_message(text, chat_id):
  send_request('sendMessage', {'chat_id': chat_id, 'text': text})

###### helpers above ####### 


def process_message(m):
  update_id = int(m.get('update_id'))
  update_offset(update_id)
  print 'Processed %s' % (update_id)
  m = m.get('message')
  if m is not None and m.get('message_id') is not None:
    m_id = m.get('mesesage_id')
    chat_id = m['chat']['id']
    if m.get('text') is not None and m['text'].find('fuck') >= 0:
      send_message('Please stop fucking.', chat_id)
    if m.get('text') is not None and m['text'].endswith('='):
      exp = m['text'][:-1]
      try:
        answer = eval(exp,{"__builtins__":None})
        send_message('%s %s' % (m['text'], answer), chat_id)
      except Exception, e:
        send_message('Cannot evaluate: %s' % str(e), chat_id)


if __name__ == '__main__':
  while True:
    update_id = get_offset()
    res = send_request('getUpdates', {'offset': update_id+1})
    process_messages(res)
    import time
    time.sleep(2)
