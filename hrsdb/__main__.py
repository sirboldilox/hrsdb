"""
hrsdb entry point for console script

Options:
    -H/--host   Address to bind the server to (127.0.0.1)
    -p/--port   The port to list on.
    -d/--debug  If set the server will be ran in debug mode with full logging
"""
import argparse

from hrsdb.config import CONFIG as config
from hrsdb.http import create_server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Address to bind to')
    parser.add_argument('-p', '--port', type=int, default=8080, help='HTTP server port')
    parser.add_argument('-d', '--debug', action='store_true', help='Run the server in debug mode')
    args = parser.parse_args()

    app = create_server()

    if args.host:
        host = args.host
    else:
        host = config.get('http', 'host')

    if args.port:
        port = args.port
    else:
        port = config.getInt('http', 'port')

    app.debug = args.debug
    app.run(host=host, port=port)


# Start main
if __name__ == '__main__':
    main()
