"""
Http server definition
"""
from flask import Flask

# Local imports
from hrsdb.http.models import load_api


def create_server():
    """Creates the flask application for running
    the HTTP database access.
    """

    app = Flask(__name__)
    load_api(app)
    return app
