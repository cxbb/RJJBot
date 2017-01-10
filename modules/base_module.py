class BaseModule:

  def _init__(self):
    self.command_specs = []

  def process_message(self, m, cmd = None):
    if not cmd:
      return None
    self.chat_id = unicode(m['chat']['id'])
    self.sender_id = m['from']['id']
    self.sender = m['from']['first_name']
    for spec in self.command_specs:
      try:
        parsed = cmd.attempt_parse(spec['spec'])
        if parsed:
          return spec['func'](parsed)
      except Exception, e:
        return u'[ERROR|%s] %s' % (self.sender, e.message)

  def tick(self):
    return None

  def help(self, cmd):
    s = '';
    for spec in self.command_specs:
      if 'desc' in spec:
        s += spec['desc'] + '\n'
    return { 'type': 'html', 'content': s }
