import sqlite3
import logging
from six import string_types

###########################################################################
#
##   A wrapper around the sqlite3 python library.
#
#    The Database class is a high-level wrapper around the sqlite3
#    library. It allows users to create a database connection and
#    write to or fetch data from the selected database. It also has
#    various utility functions such as getLast(), which retrieves
#    only the very last item in the database, toCSV(), which writes
#    entries from a database to a CSV file, and summary(), a function
#    that takes a dataset and returns only the maximum, minimum and
#    average for each column. The Database can be opened either by passing
#    on the name of the sqlite database in the constructor, or optionally
#    after constructing the database without a name first, the open()
#    method can be used. Additionally, the Database can be opened as a
#    context method, using a 'with .. as' statement. The latter takes
#    care of closing the database.
#
# source: https://gist.github.com/goldsborough/c973d934f620e16678bf
###########################################################################

class Database:

    #######################################################################
    #
    ## The constructor of the Database class
    #
    #  The constructor can either be passed the name of the database to open
    #  or not, it is optional. The database can also be opened manually with
    #  the open() method or as a context manager.
    #
    #  @param name Optionally, the name of the database to open.
    #
    #  @see open()
    #
    #######################################################################
    
    def __init__(self, name=None):
        
        self.conn = None
        self.cursor = None

        if name:
            self.open(name)


    #######################################################################
    #
    ## Opens a new database connection.
    #
    #  This function manually opens a new database connection. The database
    #  can also be opened in the constructor or as a context manager.
    #
    #  @param name The name of the database to open.
    #
    #  @see \__init\__()
    #
    #######################################################################
    
    def open(self,name):
        
        try:
            self.conn = sqlite3.connect(name);
            # self.cursor = self.conn.cursor()
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            logging.error("Error connecting to database: " + name)


    #######################################################################
    #
    ## Function to close a datbase connection.
    #
    #  The database connection needs to be closed before you exit a program,
    #  otherwise changes might be lost. You can also manage the database
    #  connection as a context manager, then the closing is done for you. If
    #  you opened the database connection with the open() method or with the
    #  constructor ( \__init\__() ), you must close the connection with this
    #  method.
    #
    #  @see open()
    #
    #  @see \__init\__()
    #
    #######################################################################
    
    def close(self):
        
        if self.conn:
            self.conn.commit()
            # self.cursor.close()
            self.conn.close()


    def __enter__(self):
        
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        
        self.close()


    #######################################################################
    #
    ## Function to fetch/query data from a database.
    #
    #  This is the main function used to query a database for data.
    #
    #  @param table The name of the database's table to query from.
    #
    #  @param columns The string of columns, comma-separated, to fetch.
    #
    #  @param limit Optionally, a limit of items to fetch.
    #
    #######################################################################

    def get(self,table,columns,limit=None):

        query = "SELECT {0} from {1};".format(columns,table)
        # self.cursor.execute(query)

        # fetch data
        # rows = self.cursor.fetchall()
        rows = self.conn.execute(query)

        return rows[len(rows)-limit if limit else 0:]


    #######################################################################
    #
    ## Utilty function to get the last row of data from a database.
    #
    #  @param table The database's table from which to query.
    #
    #  @param columns The columns which to query.
    #
    #######################################################################

    def getLast(self,table,columns):
        
        return self.get(table,columns,limit=1)[0]


    #######################################################################
    #
    ## Function to write data to the database.
    #
    #  The write() function inserts new data into a table of the database.
    #
    #  @param table The name of the database's table to write to.
    #
    #  @param columns The columns to insert into, as a comma-separated string.
    #
    #  @param data The new data to insert, as a comma-separated string.
    #
    #######################################################################
                
    def insert(self,table, conflict=None, update=None,**data):
      def q(x):
        return "(" + x + ")"

      def quote_sql_string(value):
        '''
        If `value` is a string type, escapes single quotes in the string
        and returns the string enclosed in single quotes.
        '''
        if isinstance(value, string_types):
          new_value = str(value).replace("'", "''")
          return "'{}'".format(new_value)
        return value

      query = ''
      if data:
        # needed for Py3 compatibility with the above doctests
        sorted_values = sorted(data.items(), key=lambda t: t[0])

        _keys = ", ".join(map(lambda t: t[0], sorted_values))
        _values = ", ".join(map(lambda t: str(quote_sql_string(t[1])), sorted_values))
        if not conflict is None and not update is None:
          query = ("INSERT INTO %s " % table + q(_keys) + " VALUES " + q(_values) 
          + " ON CONFLICT " + q(conflict) + " DO UPDATE SET " + update)
        else:
          query = "INSERT INTO %s " % table + q(_keys) + " VALUES " + q(_values)
          
        with self.conn:
          return self.conn.execute(query)
      else:
          ## it is an error here not to provide data to be inserted
        return None
        # query = "INSERT INTO {0} ({1}) VALUES ({2});".format(table,columns,data)


    #######################################################################
    #
    ## Function to query any other SQL statement.
    #
    #  This function is there in case you want to execute any other sql
    #  statement other than a write or get.
    #
    #  @param sql A valid SQL statement in string format.
    #
    #######################################################################

    def query(self,sql):
      with self.conn:
        return self.conn.execute(sql)

