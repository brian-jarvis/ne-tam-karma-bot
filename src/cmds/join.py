import config
import channel_manager

def join(socket, components): # !join <#channel>+
  '''Returns a string for joining the given channel(s)

  Joins a list of channels, only if the sender is an owner
  '''
  response = ''

  join_command = components['arguments'].lstrip('!').split('join ') # notice the space

  if 2 == len(join_command):
    response = []
    join_chans = []
    response.append('JOIN ')

    arg_channels = join_command[1].lstrip().split(' ')
    all_channels = channel_manager.get_all_channels()

    for channel in arg_channels:
      channel = channel.strip('\r')
      if channel not in all_channels and len(channel) and \
      '#' == channel[0] \
      and -1 == channel.find(' '): # valid channel name
          join_chans.append(channel)
          # config.channels.append(channel)
          channel_manager.record_channel(channel)

    if len(join_chans):
      response.append(','.join(join_chans))
      response.append('\r\nPRIVMSG ' + components['action_args'][0] + \
          ' :Joined: {0}'.format(', '.join(join_chans)))
    else:
      response = 'Invalid channels names, usage: !join <#channel >+'

  else:
    response = 'Usage: !join <#channel >+'

  return response
