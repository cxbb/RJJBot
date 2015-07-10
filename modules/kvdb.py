from base_module import BaseModule
import subprocess
import json
import random

class KVDBModule(BaseModule):

  DB_FILE = 'kvdb.txt'

  def __init__(self):
    self.db = {}

  def process_message(self, m):
    if m.get('text') is None:
      return None
    stripped = m['text'].strip()
    sender_id = m['from']['id']
    chat_id = unicode(m['chat']['id'])
    sender = m['from']['first_name']

    if stripped.startswith('/set '):
      stripped_again = ' '.join(stripped.split(' ')[1:]).strip()
      args = stripped_again.split(' ', 1)
      if len(args) < 2:
        return u'%s, what is the value?' % (sender)
      key = args[0]
      value = args[1].strip()
      self.put(chat_id, key, value)
      return u'Added: %s => %s' % (key, value)

    if stripped.startswith('/get '):
      key = ' '.join(stripped.split(' ')[1:]).strip()
      try:
        value = self.get(chat_id, key)
        return u'%s => %s' % (key, value)
      except Exception, e:
        return u'Key does not exist: %s' % (key)

    if stripped.startswith('/unset '):
      key = ' '.join(stripped.split(' ')[1:]).strip()
      try:
        value = self.unset(chat_id, key)
        return u'Removed key: %s' % (key)
      except Exception, e:
        return u'Key does not exist: %s' % (key)

    if stripped == '/list':
       var_list = self.list(chat_id)
       s = 'All variables: ' + ', '.join(var_list)
       return s

  def load_db(self):
    with open(KVDBModule.DB_FILE, 'r') as f:
      input = f.read()
      self.db = json.loads(input)

  def put(self, chat_id, key, value):
    self.load_db()
    chat_db = self.db.get(chat_id) or {}
    chat_db[key] = value
    self.db[chat_id] = chat_db
    with open(KVDBModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))

  def unset(self, chat_id, key):
    self.load_db()
    chat_db = self.db.get(chat_id) or {}
    del chat_db[key]
    if len(chat_db):
      self.db[chat_id] = chat_db
    elif chat_id in self.db:
      del self.db[chat_id]
    with open(KVDBModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))

  def get(self, chat_id, key):
    self.load_db()
    chat_db = self.db.get(chat_id) or {}
    return chat_db[key]

  def list(self, chat_id):
    self.load_db()
    chat_db = self.db.get(chat_id) or {}
    return chat_db.keys()
