from pickle import UNICODE
from functions import give_users_karma

def friday(components):
  '''Sends the happy friday message to give karma on a friday
  '''
  responseList = [
    'Happy\tFriday',
    'friyay',
    'Cora',
    'northeast',
    'CSMs',
    'TAMs',
    'CSAs',
    'CSEs',
    'weekend',
    'redhat',
    'coffee',
    'snow',
  ]
  
  ## build the friday message
  return give_users_karma(responseList) + "\nHappy Birthday gangrif!!!   \U0001f389\U0001f382\U0001f389\U0001f973"
