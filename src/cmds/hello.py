import cowsay
import requests
import json

def hello(components):
  '''Say hi back
  '''

  quote_str = """
  {0}
    -- {1} {2}"""

  req = requests.get('https://officeapi.dev/api/quotes/random')
  qt = json.loads(req.text).get('data')
  return cowsay.get_output_string('squirrel', quote_str.format(qt['content'], qt['character']['firstname'], qt['character']['lastname']))
  ## old just return hello to the person.  Leaving this here incase we want to respond this way again.
  # return cowsay.get_output_string('squirrel', 'Hello {0}!'.format(components['sender']))
