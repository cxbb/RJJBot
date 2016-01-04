from base_module import BaseModule
import subprocess
import json
import random

class WhoPaysModule(BaseModule):

  SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwOnKftiPtCLhSp0hOKcRKwdxIE7cU7EGsM4yrFNma5ppvRG1jG/exec'
  RESTAURANT_FILE = 'restaurants.txt'

  def __init__(self):
    self.restaurants = []
    self.sampled = []
    self.votes = {}

  def process_message(self, m):
    if m.get('text') is None:
      return None
    stripped = m['text'].strip()
    sender_id = m['from']['id']
    sender = m['from']['first_name']
    if stripped == '/lunch':
      try:
        p = subprocess.Popen(['curl', '-L', '-k', WhoPaysModule.SCRIPT_URL], stdout=subprocess.PIPE)
        out, err = p.communicate()
        obj = json.loads(out)
        who = obj['whoPays']
        amount = obj['amount']
        return 'Today {0} will pay for lunch. (Amount owed: ${1:,.1f})'.format(who, amount)
      except Exception, e:
        return 'Enjoy. Error: %s' % (str(e))

    if stripped.startswith('/eatadd '):
      restaurant_name = ' '.join(stripped.split(' ')[1:]).strip()
      self.add_restaurant(restaurant_name)
      return u'Added restaurant name [%s]' % (restaurant_name)

    if stripped.startswith('/eatremove'):
      restaurant_name = ' '.join(stripped.split(' ')[1:]).strip()
      self.remove_restaurant(restaurant_name)
      return u'Removed restaurant name [%s]' % (restaurant_name)

    if stripped == '/eatlist':
      self.load_restaurant_list()
      return ', '.join(self.restaurants)

    if stripped.startswith('/eatsample'):
      count = 5
      try:
        if stripped != '/eatsample':
          remains = stripped.split(' ', 1)[1]
          count = int(remains.strip())
          if count <= 0:
            raise Exception('')
        self.sample_k(count)
      except Exception, e:
        return 'Invalid number of restaurants.'
      return '\n'.join(['%s. %s' % (i+1, v) for i, v in enumerate(self.sampled)]) + '\nUse /eatvote [1-%s] to vote.' % (len(self.sampled))

    if stripped.startswith('/eataddsample '):
       try:
         restaurant = ' '.join(stripped.split(' ')[1:]).strip()
         if not self.add_sample ( restaurant ):
           raise Exception(e)
       except Exception, e:
         return 'Invalid Restaurant %s.' % restaurant
       return '\n'.join( ['%s. %s' % (i+1,v) for i, v in enumerate(self.sampled)]) + '\nUse /eatvote[1-%s] to vote.' % (len(self.sampled))

    if stripped.startswith('/eatvote'):
       try:
         remains = stripped.split(' ', 1)[1]
         index = int(remains.strip()) - 1
         if self.vote(sender_id, sender, index):
           return '%s voted for %s.' % (sender, self.sampled[index])
         else:
           raise Exception(e)
       except Exception, e:
         print str(e)
         return '%s: Invalid vote. Use /eatvote [1-%s]' % (sender, len(self.sampled))

    if stripped == '/eatstat':
      if len(self.sampled) <= 0:
        return 'No poll is going on.'
      return self.print_stat() + '\nUse /eatvote [1-%s] to vote.' % (len(self.sampled))

    return None

  def print_stat(self):
    num_votes = [ 0 ] * len(self.sampled)
    for vote in self.votes.values():
      num_votes[vote[1]] += 1
    return '\n'.join([ ('%s: %s' % (self.sampled[i], num_votes[i])) for i,v in enumerate(num_votes) ])

  def load_restaurant_list(self):
    with open(WhoPaysModule.RESTAURANT_FILE, 'r') as f:
      self.restaurants = f.read().decode('utf-8').splitlines()

  def add_restaurant(self, name):
    self.load_restaurant_list()
    if name in self.restaurants:
      return False
    self.restaurants += [ name ]
    with open(WhoPaysModule.RESTAURANT_FILE, 'w') as f:
      f.write('\n'.join(self.restaurants).encode('utf-8'))

  def remove_restaurant(self, name):
    self.load_restaurant_list()
    if not name in self.restaurants:
      return False
    self.restaurants.remove(name)
    with open(WhoPaysModule.RESTAURANT_FILE, 'w') as f:
      f.write('\n'.join(self.restaurants).encode('utf-8'))

  def sample_k(self, k):
    self.load_restaurant_list()
    self.sampled = random.sample(self.restaurants, k)
    self.sampled += [ u'I don\'t like these restaurants\U0001F31A' ]
    self.votes = {}

  def add_sample(self, name):
    if name in self.sampled:
      return False
    if name not in self.restaurants:
      return False
    else:
      self.sampled += [ name ]
      return True

  def vote(self, user_id, username, index):
    if index < 0 or index >= len(self.sampled):
      return False
    self.votes[user_id] = (username, index)
    return True
