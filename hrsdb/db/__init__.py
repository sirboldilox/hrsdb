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

    def __init__(self, session_class=Session):
        """Initialise a datbase connection handler

        :param session_class: Session object created from calling "sessionmaker"
                                This can be overridden for custom unit tests.
        """
        self.session = session_class()

    def __enter__(self):
        return self.session

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

