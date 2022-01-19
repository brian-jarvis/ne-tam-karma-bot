import cowsay
import requests
import json
import quote_manager

def hello(components):
  '''Say hi back
  '''

  quote_str = """
  {0}
    -- {1} {2}"""

  sqt = quote_manager.get_random_quote(quote_type=['fame'])  #, 'nerd'])
  print(quote_manager.format_print(sqt))
  return cowsay.get_output_string('squirrel', quote_manager.format_print(sqt))

  req = requests.get('https://officeapi.dev/api/quotes/random')
  qt = json.loads(req.text).get('data')
  return cowsay.get_output_string('squirrel', quote_str.format(qt['content'], qt['character']['firstname'], qt['character']['lastname']))
  ## old just return hello to the person.  Leaving this here incase we want to respond this way again.
  # return cowsay.get_output_string('squirrel', 'Hello {0}!'.format(components['sender']))
