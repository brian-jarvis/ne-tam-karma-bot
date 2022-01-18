import config
from functions import *
import logging
import requests

def weather(socket, components):
  ''' Returns the current weather for the location listed
  '''

  response = ''
  weather_url = ''
  cmd_args = components['arguments'].lstrip('!').split('weather ') # notice the space
  ## check if we need more than the current weather
  forcast_days = None if (len(cmd_args) <= 1 or len(cmd_args[1].split(' ')) <= 1) else cmd_args[1].split(' ')[1].strip()

  # cmd_args should be at least 2 elements
  if len(cmd_args)  == 1:
    ## we did not get a location
    response = 'Usage: !weather <Location> [Number_Days]'
  elif len(cmd_args) >= 2 and cmd_args[1].strip() != '':
    #  we have a location and need current weather
    forcast_location, forcast_days = [cmd_args[1].strip().split(' ')[0], None if len(cmd_args[1].strip().split(' ')) == 1 else cmd_args[1].strip().split(' ')[1]]
    weather_url = 'http://wttr.in/' + forcast_location + '?T&' + ('0' if forcast_days is None else str(forcast_days))

    ## get the weather
    logging.debug("Getting weather from url: {0}".format(weather_url))
    res = requests.get(weather_url)
    response = res.text.replace('\n', '\r\n')

    if components['action_args'] != config.current_nick and not forcast_days is None:
      ## we sent the weather request to a channel, but asked for a future forcast.
      ## we will respond direct instead, and tell the channel something else
      priv_to = "PRIVMSG {0} :".format(components['sender'])
      send_response(response, priv_to, socket)
      response = 'Extended weather forcast sent direct to {0}'.format(components['sender'])

  return response
  