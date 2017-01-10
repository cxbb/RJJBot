from base_module import BaseModule
import subprocess
import json
import random

class MemoModule(BaseModule):

  DB_FILE = 'memo.txt'

  def __init__(self):
    self.db = {}
    self.command_specs = [
      { 'spec': [ 'memo' ], 'func': self.list, 'desc': '/memo - List all memoes' },
      { 'spec': [ 'memo', 'add', ':', ':string' ], 'func': self.put, 'desc': '/memo add <i>MEMO</i> - Add a new memo' },
      { 'spec': [ 'memo', 'del', ':', ':int' ], 'func': self.unset, 'desc': '/memo del <i>MEMO_INDEX</i> - Delete a memo' },
      { 'spec': [ 'memo', 'edit', ':', ':int', ':string' ], 'func': self.edit, 'desc': '/memo edit <i>MEMO_INDEX MEMO</i> - Edit a memo' },
      { 'spec': [ 'memo', 'insert', ':', ':int', ':string' ], 'func': self.insert, 'desc': '/memo insert <i>MEMO_INDEX MEMO</i> - Insert a memo at the specified index' },
      { 'spec': [ 'memo', 'help', ':' ], 'func': self.help, 'desc': '/memo help - Show this help' },
      { 'spec': [ 'memo', ':string' ], 'func': self.unknown }, 
    ]

  def load_db(self):
    with open(MemoModule.DB_FILE, 'r') as f:
      input = f.read()
      self.db = json.loads(input)

  def put(self, cmd):
    # memo add content
    self.load_db()
    chat_db = self.db.get(self.chat_id) or []
    chat_db.append(cmd[2])
    self.db[self.chat_id] = chat_db
    with open(MemoModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))
    return u'Added memo: %s' % (cmd[2])

  def edit(self, cmd):
    # memo edit index content
    index = cmd[2] - 1
    value = cmd[3]
    self.load_db()
    chat_db = self.db.get(self.chat_id) or []
    if index < 0 or index >= len(chat_db):
      raise Exception('Memo index out of range')
    chat_db[index] = value
    self.db[self.chat_id] = chat_db
    with open(MemoModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))
    return u'Edited memo: %s' % value

  def insert(self, cmd):
    # memo insert index content
    index = cmd[2] - 1
    value = cmd[3]
    self.load_db()
    chat_db = self.db.get(self.chat_id) or []
    if index < 0 or index > len(chat_db):
      raise Exception('Memo index out of range')
    chat_db.insert(index, value)
    self.db[self.chat_id] = chat_db
    with open(MemoModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))
    return u'Inserted memo: %s' % value

  def unset(self, cmd):
    # memo del index
    index = cmd[2] - 1
    self.load_db()
    chat_db = self.db.get(self.chat_id) or []
    if index < 0 or index >= len(chat_db):
      raise Exception('Memo index out of range')
    removed = chat_db[index]
    chat_db = chat_db[:index] + chat_db[index+1:]
    if len(chat_db):
      self.db[self.chat_id] = chat_db
    elif self.chat_id in self.db:
      del self.db[self.chat_id]
    with open(MemoModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))
    return u'Removed memo: %s' % removed

  def list(self, cmd):
    # memo
    self.load_db()
    var_list = self.db.get(self.chat_id) or []
    s = 'Memo:\n'
    for i in xrange(0, len(var_list)):
      s += '[%s] %s\n' % ((i+1), var_list[i])
    return s

  def unknown(self, cmd):
    raise Exception('Unknown subcommand: %s\nType /memo help for the list of subcommands.' % (cmd[1].split()[0]))
