import cowsay
import requests
import json
import quote_manager

def hello(components):
  '''Say hi back with a random quote.
  '''
  sqt = quote_manager.get_random_quote(quote_type=['fame', 'nerd', 'nerd-excuse'])
  print(quote_manager.format_print(sqt))
  return cowsay.get_output_string('squirrel', quote_manager.format_print(sqt))

  ## old just return hello to the person.  Leaving this here incase we want to respond this way again.
  # return cowsay.get_output_string('squirrel', 'Hello {0}!'.format(components['sender']))
