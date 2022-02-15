import time
import logging

# some commands can be executed only if the user's nick is found in this list
owner = list(set([
  'bry',
  'dpathak',
]))


# server to connect to
server = 'irc.devel.redhat.com'
# server's port
port = 6667

# bot's nicknames
nicks = list(set(['KarmaBot-bry']))

# bot's real name
real_name = 'NE TAM Karma Bot'

# channel to perform management tasks with
management_channel = ''

# channels to join on startup
channels = list(set([
  '#test-karma'
]))

cmds = {
  # core commands list, these commands will be run in the same thread as the bot
  # and will have acces to the socket that the bot uses
  'core': list(set([
    'quit',
    'join',
    'channels',
    'give',
    'weather',
  ])),

  # normal commands list, the ones that are accessible to any user
  'user': list(set([
    'about',
    'help',
    'uptime',
    'friday',
    'yo',
    'hello',
  ])),

}

known_bots = list(set([
  'karma*', 
  'chanserv', 
  'red*', 
  'stampy',
  'robotnik',
]))

# database details
db_file = '/opt/sqlite/ne-tam-bot/karma_bot.sqlite'

# users should NOT modify below!
logging_level = logging.DEBUG
start_time = time.time()
current_nick = ''
