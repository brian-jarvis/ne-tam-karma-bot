from functions import give_users_karma

def friday(components):
  '''Sends the happy friday message to give karma on a friday
  '''
  responseList = [
    'Happy\tFriday',
    'friyay',
    'Cora',
    'northeast',
    'santa',
    'CSMs',
    'TAMs',
    'CSAs',
    'weekend',
    'redhat',
    'coffee',
  ]
  
  ## build the friday message
  return give_users_karma(responseList)
