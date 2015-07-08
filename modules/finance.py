from base_module import BaseModule
import subprocess
import json
import random

class FinanceModule(BaseModule):

  HSI_URL = 'http://finance.yahoo.com/webservice/v1/symbols/%5EHSI/quote?format=json&view=detail'

  def __init__(self):
    pass

  def process_message(self, m):
    if m.get('text') is None:
      return None
    stripped = m['text'].strip()
    sender_id = m['from']['id']
    sender = m['from']['first_name']
    if stripped == '/hsi':
      try:
        p = subprocess.Popen(['curl', '-L', '-k', FinanceModule.HSI_URL], stdout=subprocess.PIPE)
        out, err = p.communicate()
        obj = json.loads(out)
        hsi_price = obj['list']['resources'][0]['resource']['fields']['price']
        hsi_date = obj['list']['resources'][0]['resource']['fields']['utctime']
        return 'Hang Seng Index at %s: %s' % (hsi_date, hsi_price)
      except Exception, e:
        return 'Enjoy. Error: %s' % (str(e))

