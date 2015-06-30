from base_module import BaseModule

class BasicModule(BaseModule):

  def process_message(self, m):
    if m.get('text') is not None and m['text'].find('fuck') >= 0:
      return 'Please stop fucking.'
    if m.get('text') is not None and m['text'].endswith('='):
      exp = m['text'][:-1]
      try:
        answer = eval(exp,{"__builtins__":None})
        return '%s %s' % (m['text'], answer)
      except Exception, e:
        return 'Cannot evaluate: %s' % str(e)

    return None
