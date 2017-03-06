# coding=UTF-8
from base_module import BaseModule
import random
import urllib, json
import emoji

class HikingModule(BaseModule):

  SCRIPT_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=FDLG6NDcG9v94F8pJvctaXEldDV2W7BuRFXrhBD-RSi-WaNf_KqT5GmlpbjGwSirrhz8WUAoS0pTLxkoPJm_7A97OQbH1bqMOJmA1Yb3SEsKFZqtv3DaNYcMrmhZHmUMWojr9NvTBuBLhyHCd5hHa1RrwfDakIhMfngWNTOS05701x3PsS1mIMfL1iu-Ur7B0hvVYDPgWvG_O8T_T86mmEs05uexzwXqPyGj0Oizke38rcpeGt7mzwxDjWHXOCpSD2fb_wpd558NIQgBDNdlX2UCHPA2BNcyzd_dgT7OAiY27B8Rh4QJTQ&lib=MXcNvVeJzSjQDPPe6iqOmXnvDcbQRBK6i"
  PATHS = None

  def __init__(self):
    self.command_specs = [
      { 'spec': [ 'hiking', 'help' ], 'func': self.help, 'desc': '/hiking help - Show this help' },
      { 'spec': [ 'hiking', 'reload' ], 'func': self.renew_paths, 'desc': '/hiking reload - Reload the pahts database' },
      { 'spec': [ 'hiking', 'list'], 'func': self.list, 'desc': '/hiking list - list all paths' },
      { 'spec': [ 'hiking', ':int'], 'func': self.getPath, 'desc': '/hiking &lt;ID&gt; - Get the path suggestion with &lt;ID&gt;'},
      { 'spec': [ 'hiking', ':' ], 'func': self.getRandomPath, 'desc': '/hiking - Random get a path suggestion' },
    ]
    self.renew_paths([])

  def renew_paths(self, cmd):
    response = urllib.urlopen(self.SCRIPT_URL)
    data = json.loads(response.read())
    self.PATHS = data['sheet1']
    return "Fine"

  def get_hardness_string(self, hardness):
    unencoded_str = ':star2:' * hardness
    return emoji.emojize(unencoded_str, use_aliases=True)

  def getRandomPath(self, cmd):
    num = len(self.PATHS)
    path_idx = random.randint(1,num)
    return self.getPath([0,path_idx])

  def getPath(self,cmd):
    try:
      path_idx = cmd[1]
      if self.PATHS is None or path_idx > len(self.PATHS):
        self.renew_paths(cmd)
      if path_idx < 0 or path_idx > len(self.PATHS):
        return 'Only %d paths (1-%d)' % (len(self.PATHS), len(self.PATHS))
      path = self.PATHS[path_idx-1]
      return {'type':'html', 'content': u"路段%d：%s\n起點：%s\n終點：%s\n全長：%dkm\n估計時間：%dhr\n難度(Max. 4)：%s\n%s" % (path_idx, path['Path'], path['Endpoint1'], path['Endpoint2'], path['Distance_(km)'], path['Duration_(hr)'], self.get_hardness_string(path['Hardness_(max._=_4)']), path['Link']), 'disable_preview': False}
    except Exception, e:
      raise Exception('Enjoy. Error: %s'%(str(e)))

  def list(self,cmd):
    try:
      str = ''
      for x in xrange(0,len(self.PATHS)):
        str += "%d: %s\n" % ( x+1, self.PATHS[x]['Path'] )
      return str
    except Exception, e:
      raise Exception('Enjoy. Error: %s'%(str(e)))
