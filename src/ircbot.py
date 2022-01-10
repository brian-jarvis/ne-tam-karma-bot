#! /usr/bin/env python2.7
import sys
import signal
import concurrent.futures
import logging
import os

import config
import parser
import err
from functions import *
import channel_manager

## below breaks and crashs
# "                .88888888:."
# 2022-01-10 21:37:51 - DEBUG - ALL: :stampy!~stampy@10.44.130.145 PRIVMSG #gcs-na-northeast :                .88888888:.

# Traceback (most recent call last):
#   File "/opt/KarmaBot/ircbot.py", line 183, in <module>
#     main()
#   File "/opt/KarmaBot/ircbot.py", line 175, in main
#     run(socket, channel_list, config.cmds, config.current_nick)
#   File "/opt/KarmaBot/ircbot.py", line 62, in run
#     is_cmd_prefix = ('!' == frst_arg[0])
# IndexError: string index out of range


def run(socket, channels, cmds, nick):
  # buffer for some command received
  buff = ''
  num_workers = sum(len(v) for k, v in cmds.items())

  # TODO: what happens if I use all the workers?

  # TODO: don't let commands to run for more than one minute

  with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
    while len(channels):
      # receive = socket.recv(4096).decode()
      rv = recv_timeout(socket, 4096, 10)
      if not rv is None:
        receive = rv.decode()

        buff = buff + receive
        response = ''

        logging.debug("ALL: " + receive + \
                ('' if '\n' == receive[len(receive)-1] else '\n'))

        if -1 != buff.find('\n'):
          # get a full command from the buffer
          command = buff[0 : buff.find('\n')]
          buff = buff[buff.find('\n')+1 : ]

          # command's components after parsing
          components = parser.parse_command(command)
          to = send_to(command)

          if 'PING' == components['action']:
            response = []
            response.append('PONG')
            response.append(':' + components['arguments'])

          elif 'PRIVMSG' == components['action']:
            frst_arg = components['arguments'].strip().split(' ')[0].lower()

            ## we will accept either !<Command> as the first arg
            ## or our name followed by the command. EGG: you can also use tambot
            is_bot_prefix = any(
                              list(
                                filter(
                                  lambda bot: fnmatch.fnmatch(frst_arg, bot), list(set(['tambot*', config.current_nick.lower() + '*']))
                                )
                              )
                            )
            is_cmd_prefix = ('!' == frst_arg[0])

            sender_is_bot = any(list(filter(lambda bot: fnmatch.fnmatch(components['sender'].lower(), bot), config.known_bots)))
            if (is_cmd_prefix or is_bot_prefix) and (not sender_is_bot):

              logging.debug(receive + \
                ('' if '\n' == receive[len(receive)-1] else '\n'))

              ## if it has a bot prefix we need to remove that from the args and treat the remaining the same as 
              ## we would if it was just a !<Command> sent to us
              if is_bot_prefix:
                components['arguments'] = components['arguments'].split(' ', 1)[1]

              pos = components['arguments'].find(' ')
              if -1 == pos:
                pos = len(components['arguments'])

              # get the command issued to the bot without the "!"
              # cmd = components['arguments'][1:pos]
              cmd = components['arguments'].lstrip('!').split(' ')[0]

              callable_cmd = get_cmd(cmd, cmds['user'])
              if callable_cmd:
                run_cmd(socket, executor, to, callable_cmd, components)
              else:
                callable_cmd = get_cmd(cmd, cmds['core'])

                if callable_cmd:
                  try:
                    response = callable_cmd(socket, components)
                  except Exception as e:
                    response = err.C_EXCEPTION.format(
                    callable_cmd.__name__)

                    logging.error(str(e))
                else:
                  ## bad command supplied
                  response = "'{0}' is a bad command, try !help or {1} help".format(components['arguments'], config.current_nick)

          elif 'INVITE' == components['action'] and \
            nick == components['action_args'][0]:
            ## we have been invited to another channel
            cmd = 'join'
            components['arguments'] = '!join ' + components['arguments']

            callable_cmd = get_cmd(cmd, cmds['core'])
            try:
              response = callable_cmd(socket, components)
            except Exception as e:
              response = err.C_EXCEPTION.format(
              callable_cmd.__name__)

              logging.error(str(e))

          elif 'KICK' == components['action'] and \
            nick == components['action_args'][1]:
              ch_nm = components['action_args'][0]
              logging.info("Kicking bot from channel %s" % ch_nm)
              channels.remove(ch_nm)
              channel_manager.record_channel(ch_nm, is_active=False)

          elif 'QUIT' == components['action'] and \
                  -1 != components['arguments'].find('Ping timeout: '):
            channels[:] = []

          # this call is still necessary in case that a PONG response or a
          # core command response should be sent, every other response is
          # sent when the futures finish working from their respective
          # thread
          send_response(response, to, socket)

          buff = ''


def main():
  valid_cfg = check_cfg(config.owner, config.server, config.nicks,
                config.real_name, config.cmds)

  if not valid_cfg:
      sys.exit(err.INVALID_CFG)

  try:
    logging.basicConfig(
        level=config.logging_level,
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
  except IOError as e:
    print( "Couldn't set up logging: " + str(e))
    sys.exit(1)

  ## initialize database for managing bot
  initialize_db()

  if not check_channel(channel_manager.get_all_channels()):
    sys.exit(err.INVALID_CHANNELS)

  signal.signal(signal.SIGINT, sigint_handler)

  socket = create_socket()

  if socket and connect_to((config.server, config.port), socket):
    logging.info('Connected to {0}:{1}'.format(config.server, config.port))

    config.current_nick = name_bot(socket, config.nicks, config.real_name)
    config.management_channel = '#' + config.current_nick

    channel_list = channel_manager.get_all_channels()
    channel_list.append(config.management_channel)

    joined = join_channels(channel_list, socket)

    if joined:
        run(socket, channel_list, config.cmds, config.current_nick)

    quit_bot(socket)
    socket.close()

    logging.info('Disconnected from {0}:{1}'.format(config.server, config.port))

if '__main__' == __name__: #pragma: no cover
  main()
