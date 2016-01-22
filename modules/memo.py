from base_module import BaseModule
import subprocess
import json
import random

class MemoModule(BaseModule):

  DB_FILE = 'memo.txt'

  def __init__(self):
    self.db = {}

  def process_message(self, m):
    if m.get('text') is None:
      return None
    stripped = m['text'].strip()
    sender_id = m['from']['id']
    chat_id = unicode(m['chat']['id'])
    sender = m['from']['first_name']

    if stripped.startswith('/addmemo '):
      stripped_again = ' '.join(stripped.split(' ')[1:]).strip()
      if len(stripped_again) == 0:
        return u'Add what?????'
      self.put(chat_id, stripped_again)
      return u'Added memo: %s' % (stripped_again)

    if stripped.startswith('/delmemo '):
      stripped_again = ' '.join(stripped.split(' ')[1:]).strip()
      try:
        index = int(stripped_again)
        ret = self.unset(chat_id, index-1)
        return 'Removed memo: %s' % (ret)
      except:
        return "Failed :("

    if stripped == '/memo':
      s = 'Memo:\n'
      var_list = self.list(chat_id)
      for i in xrange(0, len(var_list)):
        s += '[%s] %s\n' % ((i+1), var_list[i])
      return s

  def load_db(self):
    with open(MemoModule.DB_FILE, 'r') as f:
      input = f.read()
      self.db = json.loads(input)

  def put(self, chat_id, value):
    self.load_db()
    chat_db = self.db.get(chat_id) or []
    chat_db.append(value)
    self.db[chat_id] = chat_db
    with open(MemoModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))

  def unset(self, chat_id, index):
    self.load_db()
    chat_db = self.db.get(chat_id) or []
    if index < 0 or index >= len(chat_db):
      raise Exception('index out of range')
    removed = chat_db[index]
    chat_db = chat_db[:index] + chat_db[index+1:]
    if len(chat_db):
      self.db[chat_id] = chat_db
    elif chat_id in self.db:
      del self.db[chat_id]
    with open(MemoModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))
    return removed

  def list(self, chat_id):
    self.load_db()
    chat_db = self.db.get(chat_id) or []
    return chat_db
