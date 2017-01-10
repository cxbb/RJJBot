from base_module import BaseModule
import random
import re
from parse import parse

###
#  /roll              - roll a die with 6 faces
#  /roll {int}        - roll a die with the specified number of faces
#  /roll {int} {int}  - roll many dice
###
class DiceModule(BaseModule):

  def __init__(self):
    self.command_specs = [
      { 'spec': [ 'roll', 'help' ], 'func': self.help, 'desc': '/roll help - Show this help' },
      { 'spec': [ 'roll' ], 'func': self.roll, 'desc': '/roll - Roll a die with 6 faces (output is 1~6)' },
      { 'spec': [ 'roll', ':int' ], 'func': self.roll, 'desc': '/roll <i>FACES</i> - Roll a die with that many faces' },
      { 'spec': [ 'roll', ':', ':int', ':int' ], 'func': self.roll, 'desc': '/roll <i>FACES REPEATS</i> - Roll a die many times' },
    ]

  def roll(self, cmd):
    faces = 6
    if len(cmd) > 1 and cmd[1] < 1:
      raise Exception('Number of faces must be positive.')
    if len(cmd) > 2 and cmd[2] < 1:
      raise Exception('Number of repeats must be positive.')
    if len(cmd) == 1:
      # /roll
      return '%s rolled a %s-sided die. Outcome = %s' % (self.sender, faces, random.randint(1, faces))
    elif len(cmd) == 2:
      # /roll FACES
      faces = cmd[1]
      return '%s rolled a %s-sided die. Outcome = %s' % (self.sender, faces, random.randint(1, faces))
    elif len(cmd) == 3:
      # /roll FACES REPEATS
      faces = cmd[1]
      times = cmd[2]
      out = [ random.randint(1, faces) for i in xrange(0, times)]
      return '%s rolled a %s-sided die %s time%s. Outcome = %s. Sum = %s' % (
        self.sender, faces, times, 's' if times > 1 else '', out, sum(out)
      )
