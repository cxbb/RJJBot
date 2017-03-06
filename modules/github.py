from base_module import BaseModule
import subprocess
import json
import random
import urllib2

class GithubModule(BaseModule):

  STATUS_URL = 'https://status.github.com/api/status.json';
  RECEIVER_ID = '-7562124'

  def __init__(self):
    self.last_status = None
    self.command_specs = [ 
        { 'spec': [ 'git', ':' ], 'func': self.get_status },
    ]

  def get_status(self, cmd):
    response = urllib2.urlopen(self.STATUS_URL)
    data = json.load(response)
    return 'Github status: ' + data['status']

  def tick(self):
    response = urllib2.urlopen(self.STATUS_URL)
    data = json.load(response)
    res = None 
    if data['status'] != self.last_status and self.last_status is not None:
        res = 'Github status: %s -> %s' % (self.last_status, data['status'])
    self.last_status = data['status']
    return res or None
