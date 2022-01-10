import config
import channel_manager

def channels(socket, components): # !channels
  '''Returns a string containing the channels the bot is connected to'''
  response = ''

  if components['arguments'].lstrip('!').lower() == 'channels':
      # the user sent just the command, no garbage
      if components['sender'] in config.owner: 
          # this command can be run only by the owners
          response = ', '.join(channel_manager.get_all_channels())
          response = config.current_nick + ' is connected to: ' + response
      else:
          response = 'This command can be run only by the owners!'

  return response
