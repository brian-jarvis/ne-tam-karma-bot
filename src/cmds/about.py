def about(components): # !about
  '''Returns a string containing info about the bot'''
  response = ''

  if components['arguments'].lstrip('!').lower() == 'about':
      # the user sent just the command, no garbage
      response = 'Bot currently maintained at https://gitlab.cee.redhat.com/bjarvis/ne-tam-karma-bot'

  return response
