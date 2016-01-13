"""
Http server definition
"""
from flask import Flask

# Local imports
from hrsdb.http.models import load_api

def create_server():
    """Creates the flask application for running the HTTP database access."""

    app = Flask(__name__)
    load_api(app)
    return app

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080, help='HTTP server port')
    parser.add_argument('-d', '--debug', action='store_true', help='Run the server in debug mode')
    args = parser.parse_args()

    app = create_server()
    app.run(port=args.port, debug=args.debug)


# Start main
if __name__ == '__main__':
    main()
