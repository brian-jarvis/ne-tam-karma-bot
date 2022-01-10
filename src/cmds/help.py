import config

def help(components): # !help
  '''Returns a string containing all the available commands'''

  response = r'''
KarmaBot was created to easily give internet points to the whole team.
  
You can issue a command using the following formats:
  karmabot <Command>
  karmabot !<Command>
  !<Command>
  
Available Commands:
  help - Displays this help message
  about - Display current information about KarmaBot
  hello - Say hi!
  yo - Because you da man!
  friday - Everyone loves Friday.  Show some love to the best day of the week (just don't tell Monday)
  give - Gives karma to every nic in the current channel
  
KarmaBot can join other channels with IRC INVITE command.  
  '''

  # if components['arguments'].lstrip('!').lower() == 'help':
  #     # the user sent just the command, no garbage
  #     response = (str(len(config.cmds['user'] + config.cmds['core'])) +
  #                 ' available commands: ')

  #     for command in config.cmds['user'] + config.cmds['core']:
  #         response = response + command + ' '

  return response
