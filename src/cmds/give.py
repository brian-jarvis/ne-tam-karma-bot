import config
from functions import *
import err
import logging
import time


def give(socket, components):
  ''' Gives karma to all users in the channel
  '''
  ## get the list of current users in the channel
  user_list = list(get_users_in_channel(components['action_args'][0], socket, True))
  logging.debug(user_list)

  ## remove the requestor from the user_list so they can't give themselves karma
  cleansed_sender = components['sender'].split('|')[0].strip('_').strip('@').strip('-')
  user_list.remove(cleansed_sender)

  ## Open a new socket to the management channel
  if len(user_list) > 0:
    try:
      ksock = create_socket()
      if ksock and connect_to((config.server, config.port), ksock):
        content = 'Connected to {0}:{1}'.format(config.server, config.port)
        logging.info(content)
        
        knick = config.current_nick + '-' + cleansed_sender + '-' + components['action_args'][0][1:]
        name_bot(ksock, [knick], config.real_name)

        ## join the management channel
        joined = join_channels([config.management_channel], ksock)

        time.sleep(2)
        ## send the message to the new channel
        send_to= 'PRIVMSG ' + config.management_channel + ' :'
        send_response(give_users_karma(user_list), send_to, ksock)
    finally:
      time.sleep(2)
      quit_bot(ksock)
      ksock.close()
    
    return components['sender'] + '\tgave\tkarma\tusing\t' + config.current_nick + '\tto\t' + '\t'.join(user_list)
  else:
    return "No users found to give karma to"
