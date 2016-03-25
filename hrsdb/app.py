"""
HTTP application

Record type definitions for the HTTP API

Returns:
    All data returned by the REST service is encoded into a JSON response object formatted as follows:
        response = {
            "response" : data
        }

    Encapsulating the response inside a Json object ensures that the top level object cannot be a list.

"""
import logging
import datetime

from flask import Flask, jsonify, abort
from flask_restful import Api, Resource, reqparse
from sqlalchemy.orm.exc import NoResultFound

# Local imports
from hrsdb import utils
from hrsdb.db import open_session, to_dict
from hrsdb.db.models import Biometric, Patient

# Logging
logger = logging.getLogger(__name__)

# Webapp
webapp = Flask(__name__)


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

        with open_session() as session:
            try:
                record = session.query(Patient) \
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
        args = self.parser.parse_args()

        # Convert data_time and validate
        date_of_birth = utils.str2date(args.date_of_birth)
        if date_of_birth is None:
            abort()

        return_id = None
        with open_session() as session:
            record = Patient(args.first_name,
                             args.last_name,
                             args.gender,
                             date_of_birth)

            session.add(record)
            session.flush()
            session.commit()

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
    API handler for returning lists of patient records
        /patients

      GET: Returns a JSON response containing a complete list of all patients
    """

    def get(self):
        """
        Fetchs the list of patient records from the database
        :return: JSON encoded list of patient records
        """
        with open_session() as session:
            try:
                records = session.query(Patient).all()
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
        api.add_resource(PatientListAPI, '/patients')


class BiometricAPI(Resource):
    """
    API handler for accessing biometric records
        /biometric/<id:int>

      GET:  Returns a JSON serialised biometric record
      PUT:  Uploads a new biometric record.
    """
    parser = reqparse.RequestParser()
    parser.add_argument('patient_id', required=True)
    parser.add_argument('biometric_type_id', required=True)
    parser.add_argument('value', type=int, required=True)
#    parser.add_argument('timestamp', required=True)

    def get(self, biometric_id):
        """GET a biometric record by ID from the database"""
        record = None
        with open_session() as session:
            try:
                record = session.session.query(Biometric) \
                    .filter(Biometric.id == biometric_id).one()
            except NoResultFound:
                logger.warn("No record found")
                return gen_response("No record found")
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

        logger.debug(record)
        return gen_response(to_dict(record))

    def put(self, biometric_id):
        """PUT a new record into the database and return the generated ID"""
        args = self.parser.parse_args()

        # Convert data_time and validate
        #timestamp = utils.str2date(args.timestamp)
        #if timestamp is None:
        #    abort()

        return_id = None
        with open_session() as session:
            try:
                patient = session.query(Patient) \
                            .filter(Patient.id == args.patient_id).one()
            except NoResultFound:
                logger.warn("PUT: No Patient matching id for biometric")
                return gen_response("No matching Patient")
            except Exception as error:
                logger.exception("Exception: %s" % (str(error)))
                return gen_response("Internal server error")

            # Add biometric record
            biometric = patient.add_biometric(session,
                                  args.biometric_type_id,
                                  args.value,
                                  #args.timestamp
                                  datetime.datetime.now()
                        )

            if biometric is None:
                logger.warn("PUT: No Patient matching id for biometric")
                return gen_response("No matching Biometric type")

            session.commit()
            return gen_response({"id": biometric.id})

    @staticmethod
    def add(api):
        api.add_resource(BiometricAPI, '/biometric/<int:biometric_id>')


class BiometricListAPI(Resource):
    """
    API handler for returning lists of biometric records for a specific patient
        /biometrics

      GET: Returns a JSON response containing a complete list of all patients
    """
    parser = reqparse.RequestParser()
    parser.add_argument('patient_id', required=True)
    parser.add_argument('biometric_type_id', required=False)

    def get(self):
        """
        Fetchs the list of biometric records from the database 
        for this patient
        :return: JSON encoded list of patient records
        """
        args = self.parser.parse_args(strict=True)

        with open_session() as session:
            try:
                query = session.query(Biometric) \
                    .filter(Biometric.patient_id == args.patient_id)
                    
                # Optional filter by type_id
                if(args.biometric_type_id):
                    query = query.filter(Biometric.type_id == args.biometric_type_id)
                
                records = query.all()

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
        api.add_resource(BiometricListAPI, '/biometrics')


# Load the api
def load_api(app):
    api = Api(app)
    for resource in Resource.__subclasses__():
        resource.add(api)


# Load the API
load_api(webapp)
