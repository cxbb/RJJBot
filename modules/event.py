from base_module import BaseModule
import subprocess
import json
import random

class EventModule(BaseModule):

  DB_FILE = 'event.txt'

  def __init__(self):
    self.db = {}
    self.chat_id = ''
    self.sender_id = ''
    self.sender_name = ''
    self.events = {}

  def break_command(self, text, num_args):
    parts = text.strip().split(None, num_args)
    command = ''
    args = []
    if len(parts) > 0:
      command = parts[0]
      if not command.startswith('/'):
        return (None, [])
      command = command[1:].split('@')[0]
      args = parts[1:]
      return (command, args)
    return (None, [])

  def process_message(self, m):
    if m.get('text') is None:
      return None
    stripped_text = m['text'].strip()
    if not stripped_text.startswith('/event'):
      return None
    self.sender_id = m['from']['id']
    self.chat_id = unicode(m['chat']['id'])
    self.sender_name = m['from']['first_name']
    (cmd, args) = self.break_command(stripped_text, 2)

    if not args:  # list events
      return 'Events:\n\n' + self.list_events()

    if args[0] == 'add':
      try:
        (cmd, args) = self.break_command(stripped_text, 3)
        self.add_event(args[1], args[2])
        return 'Added event %s' % args[1]
      except Exception, e:
        return 'Cannot add event: %s\n\nSyntax: /event add EVENTID DESCRIPTION' % e.message

    if args[0] == 'edit':
      try:
        (cmd, args) = self.break_command(stripped_text, 3)
        self.edit_event(args[1], args[2])
        return 'Updated description for event %s' % args[1]
      except Exception, e:
        return 'Cannot edit event: %s\n\nSyntax: /event edit EVENTID DESCRIPTION' % e.message

    if args[0] == 'del':
      try:
        self.del_event(args[1])
        return 'Deleted event %s' % args[1]
      except Exception, e:
        return 'Cannot delete event: %s\n\nSyntax: /event event EVENTID' % e.message

    if args[0] == 'join':
      try:
        (cmd, args) = self.break_command(stripped_text, 3)
        self.join_event(args[1], args[2] if len(args) > 2 else None)
        return 'Joined event %s' % args[1]
      except Exception, e:
        return 'Cannot join event: %s\n\nSyntax: /event join EVENTID [PARTICIPANT_NAME]' % e.message

    if args[0] == 'quit':
      try:
        (cmd, args) = self.break_command(stripped_text, 3)
        self.quit_event(args[1], args[2] if len(args) > 2 else None)
        return 'Quitted event %s' % args[1]
      except Exception, e:
        return 'Cannot quit event: %s\n\nSyntax: /event quit EVENTID [PARTICIPANT_NAME]' % e.message

    if args[0] == 'help':
      return '''Event commands:
/event
/event help
/event add EVENTID DESCRIPTION
/event edit EVENTID DESCRIPTION
/event del EVENTID
/event join EVENTID [PARTICIPANT_NAME]
/event quit EVENTID [PARTICIPANT_NAME]'''

    return 'Unknown subcommand: ' + args[0]

  def load_db(self):
    with open(EventModule.DB_FILE, 'r') as f:
      input = f.read()
      self.db = json.loads(input)
      self.events = self.db.get(self.chat_id) or {}

  def save_db(self):
    self.db[self.chat_id] = self.events
    with open(EventModule.DB_FILE, 'w') as f:
      f.write(json.dumps(self.db, ensure_ascii=False).encode('utf-8'))

  def list_events(self):
    self.load_db()
    s = ''
    for event_id in self.events:
      event = self.events[event_id]
      s += '[%s] %s\n' % (event_id, event['description'])
      for p in event['participants']:
        s += ' * %s\n' % p['name']
      s += '\n'
    return s + 'Type "/event help" for help.'

  def add_event(self, event_id, event_desc):
    self.load_db()
    if event_id in self.events:
      raise Exception('Event already exists.')
    self.events[event_id] = { 'description': event_desc, 'participants': [] }
    self.save_db()

  def edit_event(self, event_id, event_desc):
    self.load_db()
    if not event_id in self.events:
      raise Exception('Event does not exist.')
    self.events[event_id]['description'] = event_desc
    self.save_db()

  def del_event(self, event_id):
    self.load_db()
    if not event_id in self.events:
      raise Exception('Event does not exist.')
    self.events.pop(event_id, None)
    self.save_db()

  def join_event(self, event_id, user):
    self.load_db()
    if not event_id in self.events:
      raise Exception('Event does not exist.')
    participants = self.events[event_id]['participants']
    if user is not None:
      if any(p['name'] == user for p in participants):
        raise Exception('%s has already joined the event' % user)
      user_obj = { 'id': None, 'name': user }
    else:
      if any(p['id'] == self.sender_id for p in participants):
        raise Exception('You have already joined the event')
      user_obj = { 'id': self.sender_id, 'name': self.sender_name } 
    participants.append(user_obj)
    self.save_db()

  def quit_event(self, event_id, user):
    self.load_db()
    if not event_id in self.events:
      raise Exception('Event does not exist.')
    participants = self.events[event_id]['participants']
    if user is not None:
      if not any(p['name'] == user for p in participants):
        raise Exception('%s has not joined the event' % user)
      self.events[event_id]['participants'] = [ p for p in participants if p['name'] != user ]
    else:
      if not any(p['id'] == self.sender_id for p in participants):
        raise Exception('You have not joined the event')
      self.events[event_id]['participants'] = [ p for p in participants if p['id'] != self.sender_id ]
    self.save_db()
