from base_module import BaseModule
from time import gmtime, strftime
import datetime

class BasicModule(BaseModule):

  def process_message(self, m):
    if m['from']['first_name'] == 'Ho Wa':
      return ''
    if m.get('text') is not None and m['text'].strip() == '/pc':
        return 'Hi , i am going to rerun private cohort on 201 for testing purpose, it will take around 10 mins. The private cohort will not be accurate in this 10mins'
    if m.get('text') is not None and m['text'].strip() == '/time':
        now = datetime.datetime.now() + datetime.timedelta(0, 8 * 3600)  # add 8 hours
        return now.strftime('%Y-%m-%d %H:%M:%S')
    if m.get('text') is not None and m['text'].find('fuck') >= 0:
      return 'Please stop fucking.'
    if m.get('text') is not None and m['text'].strip() == '/aws':
      return 'https://937310467346.signin.aws.amazon.com/console'
    if m.get('text') is not None and m['text'].strip() == '/id':
      return 'Name: %s, ID: %s' % (m['from']['first_name'], m['from']['id'])
    if m.get('text') is not None and m['text'].endswith('='):
      exp = m['text'][:-1]
      try:
        answer = eval(exp,{"__builtins__":None})
        return '%s %s' % (m['text'], answer)
      except Exception, e:
        return 'Cannot evaluate: %s' % str(e)

    return None
