from email.quoprimime import quote
from types import SimpleNamespace
import config
from functions import *
from database import Database
import err
import logging
import random
import datetime
from dateutil import parser

class FamousQuote:
  def __init__(self):
    self.quoteId = None
    self.dateAdded = None
    self.quoteText = None
    self.author = None
    self.addedBy = None
    self.quoteType = None
    self.quoteSource = None
    self.isActive = False

  def load_from_dbRow(self, dbRow):
    """ load the instance with data from the supplied database row """
    self.quoteId = int(dbRow['quote_id'])
    self.dateAdded = parser.parse(dbRow['dt_added'])
    self.quoteText = dbRow['quote_tx']
    self.author = dbRow['author']
    self.addedBy = dbRow['added_by']
    self.quoteType = dbRow['quote_type']
    self.quoteSource = dbRow['quote_src']
    self.isActive = dbRow['is_active']

def get_random_quote(quote_type = ['fame','nerd']):
  """ Get a random quote from the quote_type specified """

  if not isinstance(quote_type, list):
    quote_type = [quote_type]

  selected_quote_type = random.choice(quote_type)

  ## get the channels recorded in the database
  with Database(config.db_file) as db:
    qt = db.query("SELECT * FROM famous_quotes where quote_type='{0}' and is_active ORDER BY RANDOM() LIMIT 1".format(selected_quote_type)).fetchall()
    if len(qt) > 0:
      fq = FamousQuote()
      fq.load_from_dbRow(qt[0])
      return fq

  return None

def format_print(quote):
  """ prints the quote based on the type """
  
  if quote.quoteType == 'nerd-excuse':
    excuse_str = """
    The cause of the problem is:
    
    {0}"""
    return excuse_str.format(quote.quoteText, quote.quoteSource)
  else:
    quote_str = """
    {0}
      -- {1}"""
    return quote_str.format(quote.quoteText, quote.author)

  
# def record_channel(channel_nm, is_active=True):
#   """ Adds the specified channel to the database so bot will always join """

#   with Database(config.db_file) as db:
#     db.insert("channel_membership", conflict="channel_nm", update='is_active=' + str(is_active), channel_nm=channel_nm)

