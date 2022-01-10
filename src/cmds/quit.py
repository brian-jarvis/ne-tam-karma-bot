import config
from functions import *
import channel_manager

def quit(socket, components): # !quit [chan_name]+ -> PART #channel
  '''Returns a string for quitting the bot from a channel(or more) or from all
  channels if no arguments are supplied

  If the user is found in the owners list then the bot is closed, otherwise a
  message is sent to the channel
  If an argument is an invalid channel name it is simply ignored
  If there are no more channels active the bot closes
  '''
  response = ''
  leave = []

  if components['sender'] in config.owner:
      response = []
      response.append('PART')

      quit_command = components['arguments'].lstrip('!').split('quit ')
      all_channels = channel_manager.get_all_channels()

      if 2 == len(quit_command): # arguments supplied
          arg_channels = quit_command[1].lstrip().split(' ')

          for chan in arg_channels:
              chan = chan.strip('\r')
              if chan in all_channels: # valid channel
                  leave.append(chan)
                  # config.channels.remove(chan)
                  channel_manager.record_channel(chan, is_active=False)


          if len(leave):
              response.append(','.join(leave))
              response.append('\r\nPRIVMSG ' +
                  components['action_args'][0] + \
                  ' :Left: {0}'.format(', '.join(leave)))
          else:
              response = 'Invalid channel names!'

      else: # no arguments supplied, quitting all channels
          response.append(','.join(all_channels))
          config.channels[:] = []
  else:
      response = 'This command can be run only by the owners!'

  return response
