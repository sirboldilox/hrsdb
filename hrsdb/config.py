"""
Config reader 
"""

import configparser

# Defaults
DEFAULT_PATH = '/etc/hrsdb.conf'

# Global config file
CONFIG = None


def load_config():
    """Load the module config"""
    config = configparser.ConfigParser()
    config.read(DEFAULT_PATH)
    return config

    
# Global config file
CONFIG = load_config()
