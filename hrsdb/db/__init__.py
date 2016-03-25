"""
General database settings
"""
import contextlib
import logging

from sqlalchemy import create_engine, event, DateTime
from sqlalchemy.orm import sessionmaker

from hrsdb import utils

# Logging
logger = logging.getLogger(__name__)

# Defaults
DEFAULT_URL = 'sqlite:///hrsdb.db'

# Global database objects
engine = None
Session = None


def init_db(config=None):
    """Initialse the database

    :param db_url: Database URL to use. If None the config is loaded
    """

    global engine, Session

    if config is None:
        db_url = DEFAULT_URL
    else:
        db_url = config.get('database', 'url', fallback=DEFAULT_URL)

    logger.info("Database URL: %s" % db_url)

    # Cleanup if called multiple times
    if Session is not None:
        Session.close_all()
    if engine is not None:
        engine.dispose()

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    # Create all database tables
    from hrsdb.db.models import Base
    Base.metadata.create_all(engine)


@contextlib.contextmanager
def open_session():
    """
    Handles connections to the database
    """
    global engine, Session

    logger.debug("DBHandler opened")
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as error:
        session.rollback()
        logger.exception("Exception: %s" % str(error))
        raise
    finally:
        session.close()


def to_dict(record):
    """
    Converts a database record into a dictionary
    :param record:  Database record
    :return:        Dictionary key=column value=value
    """
    rdict = {}
    for column in record.__table__.columns:
        value = getattr(record, column.name)

        # Convert datetime string
        if type(column.type) is DateTime:
            value = utils.date2str(value)

        rdict[column.name] = value
            
    return rdict

