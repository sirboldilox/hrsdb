"""
Common utilities for the hrsdb package
"""
import datetime

# Datetime format used for conversion
DATETIME_FORMAT = "%d/%m/%Y"

def str2date(date_string):
    """Convert a datetime string from the common format:
    dd/mm/YYYY to python Datetime
    :returns: Date string as a Datetime object, or None if there
                was conversion errors
    """
    try:
        return datetime.datetime.strptime(date_string, DATETIME_FORMAT)
    except:
        return None

def date2str(date):
    """Convert a datetime object into the common format
     as a string: dd/mm/YYYY
     :returns: Date as a string or None if there was conversion errors
    """
    try:
        return date.strftime(DATETIME_FORMAT)
    except:
        return None