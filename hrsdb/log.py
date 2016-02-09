"""
Logging for HRSDB


"""
import logging


# Log output format
LOG_FORMAT_CONSOLE = "%(asctime)s %(name)-20s %(levelname)-8s %(message)s"
LOG_FORMAT_DATE    = "%m-%d %H:%M"


def init_log():
    """Initialise system logging"""
    logging.basicConfig(level=logging.DEBUG,
                        format=LOG_FORMAT_CONSOLE,
                        datefmt=LOG_FORMAT_DATE)

    logger = logging.getLogger('hrsdb')
    logger.debug("Logging initialised")
