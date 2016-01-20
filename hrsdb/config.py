"""
Config reader 
"""

import configparser

# Config file path
DEFAULT_PATH = '/etc/hrsdb.conf'

# Default options
DEFAULTS = {
    'database': {
        'url': 'sqlite:///hrsdb.db'
    },
    'http': {
        'host': '127.0.0.1',
        'port': '8080'
    }
}

# Global config file
CONFIG = None


def load_config():
    """Load the module config"""
    config = configparser.ConfigParser(defaults=DEFAULTS)
    config.read(DEFAULT_PATH)
    return config

    
# Global config file
CONFIG = load_config()
