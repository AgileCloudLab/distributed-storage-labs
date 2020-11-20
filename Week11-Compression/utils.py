import random
import string
import os
import sqlite3

from flask import g

SQL_DB_FILENAME = "files.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            SQL_DB_FILENAME,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db
#

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
#

def init_db():
    """
    Create the DB tables
    """

    # Try to open 'create_table.sql' and execute the SQL statements in it
    with open('create_table.sql') as sqlfile:
        sql_statements = sqlfile.read().split(';')
        # Remove empty splits
        sql_statements = [s for s in sql_statements if len(s)>0]
        if not sql_statements:
            # The file is empty
            return
        
        db = sqlite3.connect(
            SQL_DB_FILENAME,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Execute each statement
        for statement in sql_statements:
            db.execute(statement)
        db.close()
#

def random_string(length=8):
    """
    Returns a random alphanumeric string of the given length. 
    Only lowercase ascii letters and numbers are used.

    :param length: Length of the requested random string 
    :return: The random generated string
    """
    return ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(length)])
#

def write_file(data, filename=None):
    """
    Write the given data to a local file with the given filename

    :param data: A bytes object that stores the file contents
    :param filename: The file name. If not given, a random string is generated
    :return: The file name of the newly written file, or None if there was an error
    """
    if not filename:
        # Generate random filename
        filename = random_string(8)
        # Add '.bin' extension
        filename += ".bin"
    
    try:
        # Open filename for writing binary content ('wb')
        # note: when a file is opened using the 'with' statment, 
        # it is closed automatically when the scope ends
        with open('./'+filename, 'wb') as f:
            f.write(data)
    except EnvironmentError as e:
        print("Error writing file: {}".format(e))
        return None
    
    return filename
#

def is_raspberry_pi():
    """
    Returns True if the current platform is a Raspberry Pi, otherwise False.
    """
    return os.uname().nodename == 'raspberrypi'
#

def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    Usage:
    for chunk in chunks(big_list, 100):
        ...
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]