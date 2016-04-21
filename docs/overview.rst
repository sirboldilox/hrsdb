Project overview
================

HRSDB implements the database design for storing health records and provides a rest based API over HTTP for reading and writing to the database.
The project is implemented in python3 for linux based systems, however should work on windows based platforms.

This api is then utilised by the 2 other components to the Health record system:
- Android record application: RecordCompanion
- Web frontend: hrsweb

The database is managed by the SQLAlchemy python package. SQLAlchemy provides a object orientated approach to
defining the database and interfacing with it. The http service is implemented using the Flask python package with
the Flask-RESTful extension. Flask provides a microframework to simplify the creation of web services while Flask-RESTful
provides interfaces to simplify the creation of REST bases systems within Flask.

Installing
----------

The project can be installed from the source root using python.

Requirements::

    python3
    python3-pip

To install the package ensure that the above packages are installed on the system using the systems package manager.
Install the project using python::

    cd <project root>
    python3 setup.py install


Configuring
~~~~~~~~~~~

An example configuration file is provided in the root of the project `local.conf` with details on all the avaliable options.

Running
-------

To run the database engine and API webserver execute the console script that is installed with the package::

    hrsdb -c <path to config file>
