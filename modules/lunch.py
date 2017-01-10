from base_module import BaseModule
import subprocess
import json
import random
import math
import datetime

class LunchModule(BaseModule):

  SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwOnKftiPtCLhSp0hOKcRKwdxIE7cU7EGsM4yrFNma5ppvRG1jG/exec'
  RESTAURANT_FILE = 'restaurants.txt'
  DB_FILE = 'lunch.txt'

  def __init__(self):
    self.restaurants = []
    self.samples = []
    self.votes = {}
    self.downvotes = {}
    self.deadline = -1
    self.load_samples()
    self.command_specs = [
      { 'spec': [ 'lunch', ':' ], 'func': self.who_pays, 'desc': '/lunch - Who pays for lunch?' },
      { 'spec': [ 'eatlist', ':' ], 'func': self.list, 'desc': '/eatlist - List all restaurants' },
      { 'spec': [ 'eatadd', ':', ':string' ], 'func': self.add, 'desc': '/eatadd <i>RESTAURANT</i> - Add a restaurant' },
      { 'spec': [ 'eatdel', ':', ':string' ], 'func': self.remove, 'desc': '/eatdel <i>RESTAURANT</i> - Remove a restaurant' },
      { 'spec': [ 'eatsample' ], 'func': self.sample, 'desc': '/eatsample <i>[NUM_SAMPLES]</i> - Sample' },
      { 'spec': [ 'eatsample', ':', ':int' ], 'func': self.sample },
      { 'spec': [ 'eatstat', ':' ], 'func': self.stat, 'desc': '/eatstat - Show vote statistics' },
      { 'spec': [ 'eatvote', ':', ':int' ], 'func': self.vote, 'desc': '/eatvote <i>INDEX</i> - Vote for your favorite restaurant' },
      { 'spec': [ 'eatdownvote', ':', ':int' ], 'func': self.downvote, 'desc': '/eatdownvote <i>INDEX</i> - Downvote your unfavorite restaurant' },
      { 'spec': [ 'eataddsample', ':', ':string' ], 'func': self.add_sample, 'desc': '/eataddsample <i>RESTAURANT</i> - Add a sample' },
      { 'spec': [ 'eatresample', ':', ':int' ], 'func': self.resample, 'desc': '/eatresample <i>INDEX</i> - Resample a choice' },
      { 'spec': [ 'eatdeadline', ':', ':int' ], 'func': self.set_deadline, 'desc': '/eatdeadline <i>HHMM</i> - Set poll to close at HH:MM. -1 for indefinite, -2 to close immediately.' },
      { 'spec': [ 'eat' ], 'func': self.help },
      { 'spec': [ 'eat', 'help' ], 'func': self.help, 'desc': '/eat help - Show this help' },
      { 'spec': [ 'eat', ':string' ], 'func': self.unknown },
    ]

  def tick(self):
    if self.deadline < 0:
      return None
    now = datetime.datetime.now()
    hour = int(math.floor(self.deadline / 100))
    minute = self.deadline % 100
    if hour == (now.hour + 8) % 24 and minute == now.minute:  # Fix time zone
      self.load_samples()
      self.deadline = -2
      self.save_samples()
      return 'NO MORE VOTES'
    return None

  def list(self, cmd):
    # /eatlist  
    self.load_restaurant_list()
    return ', '.join(self.restaurants)

  def add(self, cmd):
    # /eatadd RESTAURANT
    name = cmd[1]
    self.load_restaurant_list()
    if name in self.restaurants:
      raise Exception('Restaurant already exists: %s' % name)
    self.restaurants += [ name ]
    self.save_restaurant_list()
    return u'Added restaurant [%s]' % (name)

  def remove(self, cmd):
    # /eatremove RESTAURANT
    name = cmd[1]
    self.load_restaurant_list()
    if not name in self.restaurants:
      raise Exception('No such restaurant: %s' % name)
    self.restaurants.remove(name)
    self.save_restaurant_list()
    return u'Removed restaurant [%s]' % (name)

  def sample(self, cmd):
    # /eatsample NUM_SAMPLES
    self.load_restaurant_list()
    num_samples = cmd[1] if len(cmd) > 1 else min(5, len(self.restaurants))
    if num_samples < 1 or num_samples > len(self.restaurants):
      raise Exception('Invalid number of samples');
    self.samples = random.sample(self.restaurants, num_samples)
    self.samples += [ u'I don\'t like these restaurants\U0001F31A' ]
    self.votes = {}
    self.downvotes = {}
    self.deadline = -1
    self.save_samples()
    return '\n'.join(['%s. %s' % (i+1, v) for i, v in enumerate(self.samples)]) + '\nUse /eatvote [1-%s] to vote.' % (len(self.samples))

  def stat(self, cmd):
    # /eatstat
    self.load_samples()
    num_votes = [ 0 ] * len(self.samples)
    for vote in self.votes.values():
      num_votes[vote[1]] += 1
    for vote in self.downvotes.values():
      num_votes[vote[1]] -= 1
    s = '\n'.join([ ('%s. %s: %s' % (i+1, self.samples[i], num_votes[i])) for i,v in enumerate(num_votes) ])
    if self.deadline == -2:
      s += '\nPoll CLOSED'
    elif self.deadline != -1:
      s += '\nDeadline: %.0f:%s' % (math.floor(self.deadline/100), self.deadline%100)
    s += u'\n\u6551\u6551\20RJJ\20\u6148\u5584\u57FA\u91D1: https://twitch.streamlabs.com/jeannohs'
    return s

  def vote(self, cmd):
    # /eatvote INDEX
    index = cmd[1] - 1
    self.load_samples()
    if self.deadline == -2:
      return 'NO MORE VOTES'
    if index < 0 or index >= len(self.samples):
      raise Exception('Invalid vote')
    self.votes[str(self.sender_id)] = (self.sender, index)
    self.save_samples()
    return '%s voted for %s.' % (self.sender, self.samples[index])

  def downvote(self, cmd):
    # /eatdownvote INDEX
    index = cmd[1] - 1
    self.load_samples()
    if self.deadline == -2:
      return 'NO MORE VOTES'
    if index < 0 or index >= len(self.samples):
      raise Exception('Invalid vote')
    self.downvotes[str(self.sender_id)] = (self.sender, index)
    self.save_samples()
    return '%s downvoted %s.' % (self.sender, self.samples[index])

  def add_sample(self, cmd):
    # /eataddsample RESTAURANT
    name = cmd[1]
    self.load_samples()
    if name in self.samples:
      raise Exception('Restaurant already exists: %s' % name)
    self.samples += [ name ]
    self.save_samples()
    return '\n'.join( ['%s. %s' % (i+1,v) for i, v in enumerate(self.samples)]) + '\nUse /eatvote [1-%s] to vote.' % (len(self.samples))

  def resample(self, cmd):
    # /eatresample INDEX
    index = cmd[1] - 1
    self.load_samples()
    self.load_restaurant_list()
    if index < 0 or index >= len(self.samples):
      raise Exception('Invalid index')
    while True:
      new_sample = random.sample(self.restaurants, 1)[0]
      if new_sample == self.samples[index] or new_sample not in self.samples:
        break
    self.samples[index] = new_sample
    self.save_samples()
    return '\n'.join( ['%s. %s' % (i+1,v) for i, v in enumerate(self.samples)]) + '\nUse /eatvote [1-%s] to vote.' % (len(self.samples))

  def set_deadline(self, cmd):
    # /eatdeadline hhmm
    hour = int(math.floor(cmd[1] / 100))
    minute = cmd[1] % 100
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
      if cmd[1] < -2:
        raise Exception('Invalid time')
    self.load_samples()
    self.deadline = cmd[1]
    self.save_samples()
    if cmd[1] == -2:
      return 'Poll closed'
    elif cmd[1] == -1:
      return 'Removed poll deadline'
    return 'Deadline set: %.0f:%s' % (hour, minute)

  def who_pays(self, cmd):
    try:
      p = subprocess.Popen(['curl', '-L', '-k', LunchModule.SCRIPT_URL], stdout=subprocess.PIPE)
      out, err = p.communicate()
      obj = json.loads(out)
      # Rank 1
      idx = LunchModule.max_index(obj)
      x1 = obj[idx]
      obj = obj[:idx]+obj[idx+1:]
      who = x1['name']
      amount = x1['amount']
      # Rank 2
      idx = LunchModule.max_index(obj)
      x1 = obj[idx]
      obj = obj[:idx]+obj[idx+1:]
      who2 = x1['name']
      amount2 = x1['amount']
      # Rank 3
      idx = LunchModule.max_index(obj)
      x1 = obj[idx]
      obj = obj[:idx]+obj[idx+1:]
      who3 = x1['name']
      amount3 = x1['amount']
      # Rank 4
      idx = LunchModule.max_index(obj)
      x1 = obj[idx]
      obj = obj[:idx]+obj[idx+1:]
      who4 = x1['name']
      amount4 = x1['amount']
      # Rank 5
      idx = LunchModule.max_index(obj)
      x1 = obj[idx]
      obj = obj[:idx]+obj[idx+1:]
      who5 = x1['name']
      amount5 = x1['amount']
      return 'Today {0} will pay for lunch. (Amount owed: ${1:,.1f})'.format(who, amount) + '\n' + \
        'Backup 1: {0} (Amount owed: ${1:,.1f})'.format(who2, amount2) + '\n' + \
        'Backup 2: {0} (Amount owed: ${1:,.1f})'.format(who3, amount3) + '\n' + \
        'Backup 3: {0} (Amount owed: ${1:,.1f})'.format(who4, amount4) + '\n' + \
        'Backup 4: {0} (Amount owed: ${1:,.1f})'.format(who5, amount5)
    except Exception, e:
      raise

  @staticmethod
  def max_index(li):
    max_v = li[0]
    max_i = 0
    for i in xrange(1, len(li)):
      if li[i] > max_v:
        max_v = li[i]
        max_i = i
    return max_i

  def load_restaurant_list(self):
    with open(LunchModule.RESTAURANT_FILE, 'r') as f:
      self.restaurants = f.read().decode('utf-8').splitlines()

  def save_restaurant_list(self):
    with open(LunchModule.RESTAURANT_FILE, 'w') as f:
      f.write('\n'.join(self.restaurants).encode('utf-8'))

  def load_samples(self):
    with open(LunchModule.DB_FILE, 'r') as f:
      input = f.read().decode('utf-8')
      obj = json.loads(input)
      self.samples = obj['samples']
      self.votes = obj['votes']
      self.downvotes = obj['downvotes']
      self.deadline = obj['deadline']

  def save_samples(self):
    obj = { 'samples': self.samples, 'votes': self.votes, 'downvotes': self.downvotes, 'deadline': self.deadline }
    with open(LunchModule.DB_FILE, 'w') as f:
      f.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

  def unknown(self, cmd):
      raise Exception('Unknown subcommand: %s\nType /eat help for the list of subcommands.' % (cmd[1].split()[0]))
