"""
General database settings
"""
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# Defines
DB_URL = 'sqlite:///hrs_test.db'

# Global database objects
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)


class DBHandler(object):
    """
    Handles connections to the database
    """

    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            print("Closing session")
        else:
            print("Exeption: %s %s %s" % (str(type), str(value), str(traceback)))
        self.session.close()


def to_dict(record):
    """
    Converts a database record into a dictionary
    :param record:  Database record
    :return:        Dictionary key=column value=value
    """
    rdict = {}
    for column in record.__table__.columns:
      rdict[column.name] = str(getattr(record, column.name))

    return rdict

