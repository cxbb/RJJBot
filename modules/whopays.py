from base_module import BaseModule
import subprocess
import json

class WhoPaysModule(BaseModule):

  SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwOnKftiPtCLhSp0hOKcRKwdxIE7cU7EGsM4yrFNma5ppvRG1jG/exec'

  def process_message(self, m):
    if m.get('text') is not None and m['text'].strip() == '/lunch':
      try:
        p = subprocess.Popen(['curl', '-L', '-k', WhoPaysModule.SCRIPT_URL], stdout=subprocess.PIPE)
        out, err = p.communicate()
        print out
        obj = json.loads(out)
        who = obj['whoPays']
        amount = obj['amount']
        return 'Today {0} will pay for lunch. (Amount owed: ${1:,.1f})'.format(who, amount)
      except Exception, e:
        return 'Enjoy. Error: %s' % (str(e))

    return None
