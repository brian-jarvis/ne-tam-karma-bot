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

  if len(user_list) > 0:
    try:
      ## Open a new socket to the management channel
      ksock = create_socket()
      if ksock and connect_to((config.server, config.port), ksock):
        logging.info('Connected to {0}:{1} for karma'.format(config.server, config.port))
        
        knick = cleansed_sender + '-' + components['action_args'][0][1:] + '-' + config.current_nick 
        name_bot(ksock, [knick], config.real_name)

        ## join the management channel
        joined = join_channels([config.management_channel], ksock)

        time.sleep(2)
        ## send the message to the new channel
        send_to= 'PRIVMSG ' + config.management_channel + ' :'
        send_response(give_users_karma(user_list) + '\n', send_to, ksock)

        rv = ''
        while not rv is None:
          rv = recv_timeout(ksock, 4096, 5)
          if not rv is None:
            ms = rv.decode()
            logging.debug("KSOCK: " + ms + \
                ('' if '\n' == ms[len(ms)-1] else '\n'))
    finally:
      quit_bot(ksock)
      ksock.close()
    
    return components['sender'] + '\tgave\tkarma\tusing\t' + config.current_nick + '\tto\t' + '\t'.join(user_list)
  else:
    return "No users found to give karma to"
