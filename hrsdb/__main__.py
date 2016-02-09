"""
hrsdb entry point for console script

Options:
    -H/--host   Address to bind the server to (127.0.0.1)
    -p/--port   The port to list on.
    -d/--debug  If set the server will be ran in debug mode with full logging
"""
import argparse
import logging

from hrsdb.config import CONFIG as config
from hrsdb.log import init_log
from hrsdb.http import create_server

# Log handler
logs = logging.getLogger(__name__)

# Defaults
DEFAULT_HTTP_HOST = '127.0.0.1'
DEFAULT_HTTP_PORT = '8080'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Address to bind to')
    parser.add_argument('-p', '--port', type=int, help='HTTP server port')
    parser.add_argument('-d', '--debug', action='store_true', help='Run the server in debug mode')
    args = parser.parse_args()

    # Setup logging
    init_log()

    app = create_server()

    # Check config order (cli > config > defaults)
    if args.host:
        host = args.host
    else:
        host = config.get('http', 'host', fallback=DEFAULT_HTTP_HOST)

    if args.port:
        port = args.port
    else:
        port = int(config.get('http', 'port', fallback=DEFAULT_HTTP_PORT))

    app.debug = args.debug
    app.run(host=host, port=port)


# Start main
if __name__ == '__main__':
    main()
