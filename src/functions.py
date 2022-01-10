import config
import err
import datetime
import socket
import threading
import os
import logging
import fnmatch
from database import Database

## function to wrap irc messages in
irc_fmt = lambda x: bytes(x, "UTF-8")
give_users_karma = lambda x: "++\t".join(x) + '++'

def get_sender(msg):
    "Returns the user's nick (string) that sent the message"
    return msg.split(":")[1].split('!')[0]


def get_datetime():
    '''Returns a dictionary containing the date and time

    dt['time'] - contains current time in hh:mm format(24 hrs)
    dt['date'] - contains current date as dd-mm-yyyy format
    '''
    dt = {}

    now = datetime.datetime.now()
    dt['time'] = now.strftime('%H:%M')
    dt['date'] = now.strftime('%d-%m-%Y')

    return dt


def check_cfg(*items):
    '''Checks configuration directives to be non-empty

    Returns True if all configuration directives are not empty, else returns False
    '''
    for arg in items:
        if not len(arg):
            return False

    return True


def check_channel(channels):
    '''Check the channels' name to start with a '#' and not to contain any spaces

    Returns True if all channels' name are valid, else False
    '''
    for channel in channels:
        if '#' != channel[0] or -1 != channel.find(' '):
            return False

    return True


def send_to(command):
    '''Get the location where to send the message back

    This function returns a string containing all the protocol related
    information needed by the server to send the command back to the
    user/channel that sent it
    '''
    sendto = '' # can be a user's nick(/query) or a channel

    if -1 != command.find('PRIVMSG ' + config.current_nick + ' :'):
        # the command comes from a query
        sendto = get_sender(command)
    else: # the command comes from a channel
        command = command[command.find('PRIVMSG #'):]
        command = command[command.find(' ')+1:]
        sendto = command[:command.find(' ')]

    return 'PRIVMSG ' + sendto + ' :'


def get_nick(nicks):
    for nick in nicks:
        yield nick


def sigint_handler(signalnum, frame):
    '''This function handles the CTRL-c KeyboardInterrupt
    '''

    if 'irc' in frame.f_globals.keys():
        try:
            frame.f_globals['irc'].close()
        except:
            pass

    content = 'Closing: CTRL-c pressed!'

    logging.info(content)
    print( '\n' + content)

def name_bot(irc, nicks, real_name):
    '''Try to name the bot in order to be recognised on IRC

    irc - an opened socket
    nicks - a list of strings to choose the nick from
    real_name - bot's real name

    Return the name of the bot
    '''

    import random
    import string

    nick_generator = get_nick(nicks)
    nick = next(nick_generator)
    irc.send(irc_fmt('USER ' + nick + ' ' + nick + \
            ' ' + nick + ' :' + real_name + '\r\n'))

# self.irc.send(bytes("USER " + botnick + " " + botnick +" " + botnick + " :python\n", "UTF-8"))

    logging.info('Set nick to: {0}\n'.format(nick))
    irc.send(irc_fmt('NICK ' + nick + '\r\n'))

    while True:
        receive = irc.recv(4096).decode().split('\r\n')

        if 'Nickname is already in use' in receive: # try another nickname
            try:
                nick = next(nick_generator)
            except StopIteration: # if no nick is available just make one up
                nick = nick + ''.join(random.sample(string.ascii_lowercase, 5))

            irc.send(irc_fmt('NICK ' + nick + '\r\n'))

            content = 'Changing nick to: {0}\n'.format(nick)
            logging.info(content)
        elif any(nick in n for n in receive) or any('MOTD' in r for r in receive):
            # successfully connected
            return nick


def create_socket(family=socket.AF_INET, t=socket.SOCK_STREAM, proto=0):
    '''Returns an unix socket or logs the failure message and returns None'''
    try:
        irc = socket.socket(family, t, proto)
    except IOError as e:
        message =  '{0}\n{1}'.format(err.NO_SOCKET, e)
        logging.error(message)
        return None

    return irc


def connect_to(address, s):
    '''Connect to the specified address through s (a socket object)

    Returns True on success else False
    '''
    try:
        s.connect(address)
    except IOError as e:
        content = 'Could not connect to {0}\n{1}'.format(address, e)
        logging.error(content)
        return False

    return True


def join_channels(channels, s):
    '''Send a JOIN command to the server through the s socket
    The variable 'channels' is a list of strings that represend the channels to
    be joined (including the # character)

    Returns True if the command was sent, else False
    '''
    clist = ','.join(channels)

    try:
      s.send(irc_fmt('JOIN ' + clist + '\r\n'))
    except IOError as e:
      content = 'Unexpected error while joining {0}: {1}'.format(clist, e)
      logging.error(content)
      return False

    content = 'Joined: {0}'.format(clist)
    logging.info(content)

    return True

def quit_bot(s):
    '''Send the QUIT commmand through the socket s

    Return True if the command was sent, else False
    '''

    try:
        s.send(irc_fmt('QUIT\r\n'))
    except IOError as e:
        content = 'Unexpected error while quitting: {0}'.format(e)
        logging.error(content)
        print( content)

        return False

    logging.info('QUIT')

    return True


def get_cmd(cmd, cmds_list):
    '''Search the command (cmd), eg. !twitter in the commands list (cmds_list)
    and try to import its module

    The return value is the function that represents the command or None if the
    command doesn't exist or it's not defined properly
    '''
    if cmd not in cmds_list:
        return None

    try: # the command's module needs to be imported from 'cmds/'
        mod = 'cmds.' + cmd
        mod = __import__(mod, globals(), locals(), [cmd])
    except ImportError as e: # inexistent module
        logging.error(err.C_INEXISTENT.format(cmd) + str(e))
        return None

    try:
        # the name of the command is translated into a function's name,
        # then returned
        callable_cmd = getattr(mod, cmd)
    except AttributeError as e:
        # function not defined in module
        logging.error(err.C_INVALID.format(cmd) + str(e))
        return None

    return callable_cmd


def run_cmd(sock, executor, to, cmd, arguments):
    '''Create a future object for running a command asynchronously and add a
    callback to send the response of the command back to irc
    '''
    def cb(f):
        try:
            response = f.result()
        except Exception as e: # TODO: raise a specific exception form the cmds
            response = err.C_EXCEPTION.format(cmd.__name__)
            logging.error(e)

        send_response(response.replace('\n', '\r\n'), to, sock)

    future = executor.submit(cmd, arguments)
    future.add_done_callback(cb)


send_response_lock = threading.Lock()
def send_response(response, destination, s):
  '''Attempt to send the response to destination through the s socket
  The response can be either a list or a string, if it's a list then it
  means that the module sent a command on its own (eg. PART)

  The destination can be passed using the send_to function

  True is returned upon sending the response, None if the response was empty
  or False if an error occurred while sending the response
  '''
  if response is not None and len(response): # send the response and log it
      if type(response) == type(str()):
          # the module sent just a string so
          # I have to compose the command

          # a multi-line command must be split
          crlf_pos = response[:-2].find('\r\n')
          while -1 != crlf_pos:
              crlf_pos = crlf_pos + 2 # jump over '\r\n'
              response = response[:crlf_pos] + \
                      destination + response[crlf_pos:]

              next_crlf_pos = response[crlf_pos:-2].find('\r\n')
              if -1 != next_crlf_pos:
                  crlf_pos = crlf_pos + next_crlf_pos
              else:
                  crlf_pos = -1

          response = destination + response
      else: # the module sent a command like WHOIS or KICK
          response = ' '.join(response)

      # append CRLF if not already appended
      if '\r\n' != response[-2:]:
          response = response + '\r\n'

      try:
          with send_response_lock:
              s.send(irc_fmt(response))
      except IOError as e:
          logging.error('Unexpected error while sending the response: {0}\n'
              .format(e))
          return False

      logging.debug('BotRsp:: ' + response)
      return True
  return None

def get_users_in_channel(channel, s, clean_nics = False):
  RPL_NAMREPLY   = '353'
  RPL_ENDOFNAMES = '366'
  read_buffer = ''
  names = []

  logging.debug('\r\n Starting to get names from channel ' + channel)
  s.send(irc_fmt("NAMES " + channel + "\n"))
  while True:
    read_buffer += s.recv(2048).decode()
    lines = read_buffer.split('\r\n')
    read_buffer = lines.pop()  ## This line seems useless?
    for line in lines:
      response = line.rstrip().split(' ', 3)
      response_code = response[1]
      if response_code == RPL_NAMREPLY:
        for nm in reversed(response[3].split(':')[1].split(' ')):
          if clean_nics:
            ## clean up the names, remove any |***, strip capes, strip @
            nm = nm.split('|')[0].strip('_').strip('@').strip('-')

          ## check if nick in restricted list before returning
          if not any(list(
                filter(
                  lambda bot: fnmatch.fnmatch(nm.lower(), bot), config.known_bots))):
            yield nm

    if response_code == RPL_ENDOFNAMES:
      return

def initialize_db():
  """ Creates the database use by the bot
      Ensures schema exists and applies changes on bot startup """
  logging.info("Starting database initialization")
  py_dir = os.path.dirname(__file__)

  with Database(config.db_file) as db:

    ## check if the statemanager table is there
    with open(os.path.join(py_dir, "schema/db.statemanager.sql")) as f:
      db.query(f.read())
      # db.commit()
      
    sm_table = db.query("select max(db_version) as max_version from statemanager").fetchone()
  
    ## update the database with each sql file based on what is returned from sm_table
    current_db_version = -1
    max_version = None if sm_table is None else sm_table['max_version']
    if max_version is not None:
      current_db_version = int(max_version)

    logging.debug("Current DB schema version: {}".format(current_db_version))
    
    for file in os.listdir(os.path.join(py_dir, 'schema')):
      if fnmatch.fnmatch(file, '[0-9]*.sql'):
        logging.debug(file)

        file_num = file.split('.')
        f_num = file_num[0]
        logging.debug("file numer is {}".format(f_num))
        if int(f_num) > current_db_version:
          logging.info("Applying sql from: {}".format(file))
          with open(os.path.join(py_dir, "schema/" + file)) as f:
            db.query(f.read())
            logging.debug("Increasing DB schema to: {}".format(f_num))
            db.insert("statemanager", db_version=int(f_num))
            # db.commit()

    logging.info("Completed initialization of DB")
