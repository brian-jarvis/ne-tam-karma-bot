import config
from functions import *
from database import Database
import err
import logging


def get_all_channels():
  """ Read all channes in config and existing database and join bot """

  ## get the channels hardcoded in the config
  # channel_list = list(map(lambda r: r, config.channels))
  channel_list = list(config.channels)

  ## get the channels recorded in the database
  with Database(config.db_file) as db:
    db_channel_list = db.query('SELECT channel_nm FROM channel_membership where is_active').fetchall()
    if db_channel_list is not None:
      channel_list +=  map(lambda r: r['channel_nm'], db_channel_list)

  return channel_list

def record_channel(channel_nm, is_active=True):
  """ Adds the specified channel to the database so bot will always join """

  with Database(config.db_file) as db:
    db.insert("channel_membership", conflict="channel_nm", update='is_active=' + str(is_active), channel_nm=channel_nm)

