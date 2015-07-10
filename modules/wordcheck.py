# coding=UTF-8
from base_module import BaseModule
import subprocess
import json
import random

class WordCheckModule(BaseModule):

  def __init__(self):
    self.restaurants = []
    self.sampled = []
    self.votes = {}
    self.dictionaries = { }
    self.max_length = 0
    self.report_pair = []
    with open ('MPW.txt', 'r') as f:
      wordLists = f.read().decode('utf-8').splitlines()
    for lines in wordLists:
      word, replace = lines.split(' ')
      self.max_length = max ( self.max_length, len(replace) )
      self.dictionaries[replace] = word

  def process_message(self, m):
    
    if m.get('text') is None:
      return None
    stripped = m['text'].strip()
    sender_id = m['from']['id']
    sender = m['from']['first_name']

    if stripped.startswith('/check '):
      self.report_pair = []
      msg = ' '.join(stripped.split(' ')[1:]).strip()
      ret = self.replace_word (self.replace_word ( msg, 1, 1 ), 2, self.max_length )
      return ret

    if stripped.startswith('/report'):
      ret = ''
      if len ( self.report_pair ) == 0:
        return "No Report\n"
      for ( wrong, correct ) in self.report_pair:
        ret += u'%s => %s\n' % ( wrong, correct )
      return ret

  def replace_word (self, msg, low, up):
      ret = ''
      skip = 0
      for idx in xrange ( 0, len ( msg ) ):
        if skip > 0:
          skip -= 1
          continue
        ext = True
        for i in xrange ( up, low-1, -1  ) :
          wrong = msg[idx:(idx+i)]
          if self.dictionaries.get ( msg[idx:(idx+i)] ) is not None:
            correct = self.dictionaries[wrong]
            ret += correct
            if ( wrong, correct ) not in self.report_pair:
              self.report_pair.append( (wrong, correct) )
            skip = i - 1
            ext = False
            break
        if ext:
          ret += msg[idx]
      return ret

    
