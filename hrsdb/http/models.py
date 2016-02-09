"""
Record type definitions for the HTTP API

Returns:
    All data returned by the REST service is encoded into a JSON response object formatted as follows:
        response = {
            "response" : data
        }

    Encapsulating the response inside a Json object ensures that the top level object cannot be a list.

"""
import logging

from flask import jsonify, abort
from flask_restful import Api, Resource, reqparse
from sqlalchemy.orm.exc import NoResultFound

# Local imports
from hrsdb import utils
from hrsdb.db import DBHandler, to_dict
from hrsdb.db.models import Patient

# Logging
logger = logging.getLogger(__name__)


def gen_response(data):
    """Return a JSON encoded response object for flask"""
    return jsonify({
                "response": data
            })


class PatientAPI(Resource):
    """
    API handler for accessing patient records
        /patient/<id:int>

      GET:  Returns a JSON serialised patient record
      PUT:  Uploads a new patient record.
      POST: Updates a patient record
    """

    # Parser for PUT requests
    parser = reqparse.RequestParser()
    parser.add_argument('first_name', required=True)
    parser.add_argument('last_name', required=True)
    parser.add_argument('gender', type=int, required=True)
    parser.add_argument('date_of_birth', required=True)

    def get(self, patient_id):
        """GET a patient record by ID from the database

        :returns: JSON response object
        """

        with DBHandler() as db_han:
            try:
                record = db_han.query(Patient) \
                    .filter(Patient.id == patient_id).one()
            except NoResultFound:
                logger.info("No record found")    # TODO: remove debugging
                return gen_response("No record found")
            except Exception as error:
                print("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            return gen_response(to_dict(record))

    def put(self, patient_id):
        """PUT a new record into the database and return the generated ID"""
        print("HTTP-API PATIENT PUT:")
        args = self.parser.parse_args(strict=True)

        # Convert data_time and validate
        date_of_birth = utils.str2date(args.date_of_birth)
        if date_of_birth is None:
            abort()

        return_id = None
        with DBHandler() as db_han:
            record = Patient(args.first_name,
                             args.last_name,
                             args.gender,
                             date_of_birth)

            db_han.add(record)
            db_han.flush()
            db_han.commit()

            return_id = record.id

        # Check for error handling
        if return_id is None:
            return gen_response("internal server error")
        else:
            return gen_response({"id": return_id})

    @staticmethod
    def add(api):
        api.add_resource(PatientAPI, '/patient/<int:patient_id>')


class PatientListAPI(Resource):
    """
    API handler for returning lists of patient
    records
    """

    def get(self):
        """
        Fetchs the list of patient records from the database
        :return: JSON encoded list of patient records
        """
        with DBHandler() as db_han:
            try:
                records = db_han.query(Patient).all()
            except NoResultFound:
                logger.info("No record found")    # TODO: remove debugging
                return gen_response("No result found")
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            # Build the response list
            rlist = [to_dict(record) for record in records]
            return gen_response(rlist)

    @staticmethod
    def add(api):
        api.add_resource(PatientListAPI, '/patient')


# Load the api
def load_api(app):
    api = Api(app)
    app.logger.debug("* Loading API:")
    for resource in Resource.__subclasses__():
        app.logger.debug("  -> %s" % resource.__name__)
        resource.add(api)
