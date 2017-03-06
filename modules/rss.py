from base_module import BaseModule
import subprocess
import json
import random
import math
import datetime
import feedparser

class RssModule(BaseModule):

  RSS_URL = 'https://www.genomeweb.com/channel/16/rss'
  TICK_HOUR = 9
  PUBLISH = False

  def __init__(self):
    self.deadline = -1
    self.deadline_remind = 0
    self.command_specs = [
      { 'spec': [ 'news', ':' ], 'func': self.send_news, 'desc': '/news - Sequencing News from Genome Web' },
      { 'spec': [ 'news', 'help'], 'func': self.help, 'desc': '/news help - Show this help'},
      { 'spec': [ 'news', ':string' ], 'func': self.unknown },
    ]

  def tick(self):
    now = datetime.datetime.now()
    if now.hour == 1: # 9 o'clock
      self.PUBLISH = True
      return None
    if self.PUBLISH and now.hour == 2 and now.weekday() < 5 and now.weekday() >= 0: # 10 o'clock
      self.PUBLISH = False
      return self.send_news(None)
    return None

  def send_news(self, cmd):
     feed = feedparser.parse(self.RSS_URL)
     newest = feed["items"][0]
     return {'type': 'html', 'content': newest['title'] + "\n" + newest['link'], 'disable_preview': False }

  def unknown(self, cmd):
      raise Exception('Unknown subcommand: %s\nType /news help for the list of subcommands.' % (cmd[1].split()[0]))
