class CommandParseException(Exception):
  def __init__(self, error_token_index, error_token, message):
    super(CommandParseException, self).__init__(message)
    self.error_token = error_token
    self.error_token_index = error_token_index


class Command:

  def __init__(self, text):
    trimmed_text = text.lstrip()
    if not trimmed_text.startswith('/'):
      raise CommandParseException(-1, '', 'Not a command')
    self.text = trimmed_text
    self.tokens = trimmed_text.split()
    self.tokens[0] = self.tokens[0].split('@')[0][1:]

  def attempt_parse(self, spec):
    '''Examples of spec:
         [ 'eat', 'lunch' ]
         [ 'eat', 'vote', ':int' ]
         [ 'memo', 'edit', ':int', ':string' ]
         [ 'event', 'add', ':token', ':string?' ]
    '''
    next_token = 0
    sudden_death = False
    parsed_command = []
    for (i, val) in enumerate(spec):
      if val == ':':
        sudden_death = True
        continue
      if next_token >= len(self.tokens):
        if sudden_death:
          if val == ':string?':
            parsed_command.append('')
            break
          else:
            raise CommandParseException(next_token, '', "Not enough arguments")
        else:
          return False
      if val == ':int':
        try:
          int_token = int(self.tokens[next_token])
          parsed_command.append(int_token)
          next_token += 1
        except:
          if sudden_death:
            raise CommandParseException(next_token, self.tokens[next_token], "Argument should be an integer: %s" % self.tokens[next_token])
          else:
            return False
      elif val == ':token':
        parsed_command.append(self.tokens[next_token])
        next_token += 1
      elif val == ':string' or val == ':string?':
        s = self.text.split(' ', next_token)[-1]
        parsed_command.append(s)
        next_token = len(self.tokens)
        break
      else:
        if self.tokens[next_token] != val:
          return False
        parsed_command.append(val)
        next_token += 1
    if next_token < len(self.tokens):
      if sudden_death:
        raise CommandParseException(next_token, self.tokens[next_token], "Extraneous argument: %s" % self.tokens[next_token])
      else:
        return False
    self.parsed_command = parsed_command
    return self.parsed_command


if __name__ == '__main__':
  cmd = Command(' /eat vote   2 intsfsdg 7')
  print cmd.tokens
  try:
    print cmd.attempt_parse(['eat', 'vote', ':', ':token', ':int', ':string?'])
  except CommandParseException, e:
    print 'Error: %s' % e.message
