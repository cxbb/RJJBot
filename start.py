#!/usr/bin/env python
import httplib
import urllib
import json
from modules.basic_module import BasicModule
from modules.dice import DiceModule
from modules.whopays import WhoPaysModule
from modules.finance import FinanceModule

class RJJBot:

  SERVER = 'api.telegram.org'
  with open('api-key.txt', 'r') as f:
    key = f.read().strip()
  BOT = '/bot%s/' % (key)
  OFFSET_FILE = 'offset.txt'

  def __init__(self):
    self.modules = []

  def send_request(self, method, data={}):
    c = httplib.HTTPSConnection(self.SERVER)
    params = urllib.urlencode(data)
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    try:
      c.request('POST', self.BOT + method, params, headers)
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
    except Exception, e:
      print "Exception! %s" % (str(e))


  def update_offset(self, offset):
    x = self.get_offset()
    if offset > x:
     with open(self.OFFSET_FILE, 'w') as f:
       f.write(str(offset))

  def get_offset(self):
    with open(self.OFFSET_FILE, 'r') as f:
      x = f.read()
      return int(x)

  def process_messages(self, messages):
    for message in messages:
      self.process_message(message)

  def send_message(self, text, chat_id):
    self.send_request('sendMessage', {'chat_id': chat_id, 'text': text.encode('utf-8') })

###### helpers above #######


  def process_message(self, m):
    update_id = int(m.get('update_id'))
    self.update_offset(update_id)
    print 'Processed %s' % (update_id)
    m = m.get('message')
    if m is not None and m.get('message_id') is not None:
      m_id = m.get('mesesage_id')
      chat_id = m['chat']['id']

      # Delegate messages to modules
      for module in self.modules:
        reply = module.process_message(m)
        if reply != None:
          self.send_message(reply, chat_id)
          return


  def start(self):
    print "RJJ Standby"
    while True:
      update_id = self.get_offset()
      res = self.send_request('getUpdates', { 'offset': update_id + 1 })
      self.process_messages(res)
      import time
      time.sleep(1)
    print "RJJ Close"


if __name__ == '__main__':
    rjj = RJJBot()
    rjj.modules = [BasicModule(), DiceModule(), WhoPaysModule(), FinanceModule()]
    rjj.start()

