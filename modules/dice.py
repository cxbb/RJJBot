from base_module import BaseModule
import random
import re
from parse import parse

'''
  /roll              - roll a die with 6 faces
  /roll {int}        - roll a die with the specified number of faces
  /roll {int} {int}  - roll many dice
'''
class DiceModule(BaseModule):

  def process_message(self, m):
    text = m.get('text')
    if text is None:
      return None
    sender = m['from']['first_name']
    text = re.sub(' +', ' ', text).strip() # strip multiple spaces
    ###### two arguments ######
    try:
      res = parse('/roll {:d} {:d}', text)
    except:
      res = None
    if res:
      faces = res.fixed[0]
      times = res.fixed[1]
      if faces >= 1 and times >= 1:
        out = [ random.randint(1, faces) for i in xrange(0, times)]
        return '%s rolled %s. The sum is %s.' % (sender, out, sum(out))
      else:
        return 'Positive numbers please.'
    ###### one argument ######
    try:
      res = parse('/roll {:d}', text)
    except:
      res = None
    if res:
      faces = res.fixed[0]
      if faces >= 1:
        return '%s rolled %s.' % (sender, random.randint(1, faces))
      else:
        return 'A positive number please.'
    ###### zero argument ######
    if text == '/roll':
      faces = 6
      return '%s rolled %s.' % (sender, random.randint(1, faces))
    return None
