from base_module import BaseModule
import subprocess
import json
import random

class FinanceModule(BaseModule):

  QUOTE_URL = { 'hsi': 'http://finance.yahoo.com/webservice/v1/symbols/%5EHSI/quote?format=json&view=detail',
                'nasdaq': 'http://finance.yahoo.com/webservice/v1/symbols/%5EIXIC/quote?format=json&view=detail', }

  def __init__(self):
    pass

  def process_message(self, m):
    if m.get('text') is None:
      return None
    stripped = m['text'].strip()
    sender_id = m['from']['id']
    sender = m['from']['first_name']
    if stripped == '/hsi' or stripped == '/nasdaq':
      try:
        p = subprocess.Popen(['curl', '-L', '-k', FinanceModule.QUOTE_URL[stripped[1:]]], stdout=subprocess.PIPE)
        out, err = p.communicate()
        obj = json.loads(out)
        price = obj['list']['resources'][0]['resource']['fields']['price']
        name = obj['list']['resources'][0]['resource']['fields']['name']
        date = obj['list']['resources'][0]['resource']['fields']['utctime']
        return '%s at %s: %s' % (name, date, price)
      except Exception, e:
        return 'Enjoy. Error: %s' % (str(e))

