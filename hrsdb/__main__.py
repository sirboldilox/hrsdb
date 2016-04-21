"""
hrsdb entry point for console script

Options:
    -H/--host   Address to bind the server to (127.0.0.1)
    -p/--port   The port to list on.
    -d/--debug  If set the server will be ran in debug mode with full logging
"""
import argparse
import logging
from configparser import Error as ConfigError

from hrsdb.app import webapp
from hrsdb.config import SiteConfig
from hrsdb.db import init_db
from hrsdb.log import init_log

# Log handler
logs = logging.getLogger(__name__)

# Defaults
DEFAULT_HTTP_HOST = '127.0.0.1'
DEFAULT_HTTP_PORT = 8080

DEFAULT_CONFIG_PATH = '/etc/hrsdb.conf'
DEFAULT_UPLOAD_FOLDER = '/tmp/hrsdb_uploads'


def main():
    """Service entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bind', help='Address to bind to')
    parser.add_argument('-p', '--port', type=int, help='HTTP server port')
    parser.add_argument('-c', '--config', help='Config file to load')
    parser.add_argument('-d', '--debug', action='store_true', help='Run the server in debug mode')
    args = parser.parse_args()

    # Setup logging
    init_log()

    # Setup database handler
    init_db()

    # Setup config
    if args.config:
        config_file = args.config
    else:
        config_file = DEFAULT_CONFIG_PATH
    
    try:
        config = SiteConfig.from_file(config_file)
    except ConfigError as error:
        logs.error("Exception when loading config file: %s", str(error))
        return

    # Check config order (cli > config > defaults)
    if args.bind:
        host = args.bind
    else:
        host = config.get('flask', 'bind', fallback=DEFAULT_HTTP_HOST)

    if args.port:
        port = args.port
    else:
        port = config.getint('flask', 'port', fallback=DEFAULT_HTTP_PORT)

    if args.debug:
        webapp.debug = True
    else:
        webapp.debug = config.getboolean('flask', 'debug', fallback=False)

    webapp.config['UPLOAD_FOLDER'] = config.get('flask', 'upload_folder', fallback=DEFAULT_UPLOAD_FOLDER)
    webapp.run(host=host, port=port)


# Start main
if __name__ == '__main__':
    main()
