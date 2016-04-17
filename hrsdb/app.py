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
from hrsdb.db.models import Biometric, BiometricType, ECG, Patient

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
    """API handler for accessing patient records: /patient/<id:int>"""

    # Parser for PUT requests
    parser = reqparse.RequestParser()
    parser.add_argument('first_name', required=True)
    parser.add_argument('last_name', required=True)
    parser.add_argument('gender', type=int, required=True)
    parser.add_argument('date_of_birth', required=True)

    def get(self, patient_id):
        """GET a patient record by ID from the database

        :param int patient_id: ID of the patient to search for.
        :returns:              Patient record in a response object
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
        """PUT a new record into the database
        
        :param int patient_id:   Ignored, used for GET requests
        :returns:                Database ID for the patient in a response object
        """
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
    """API handler for returning lists of patient records: /patients"""

    def get(self):
        """
        Fetchs the list of patient records from the database

        :return: JSON reponse object containing a list of all patient records
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


class BiometricTypeAPI(Resource):
    """API handler for accessing biometric types (static)

      Endpoint:  /biometric_types

      Methods:
        GET:  Returns all biometric types as JSON
    """

    def get(self):
        """GET a biometric record by ID from the database

        :param int biometric_id: ID of the biometric to search for.
        :return: JSON reponse object containing a biometric
        """
        records = None
        with open_session() as session:
            try:
                records = session.query(BiometricType).all()
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            logger.debug(records)
            rlist = [to_dict(record) for record in records]
            return gen_response(rlist)

    @staticmethod
    def add(api):
        api.add_resource(BiometricTypeAPI, '/biometric_types')


class BiometricAPI(Resource):
    """API handler for accessing biometric records

      Endpoint:  /biometric/<id:int>

      Methods:
        GET:  Returns a JSON serialised biometric record
        PUT:  Uploads a new biometric record.
    """
    parser = reqparse.RequestParser()
    parser.add_argument('patient_id', required=True)
    parser.add_argument('biometric_type_id', required=True)
    parser.add_argument('value', required=True)
    parser.add_argument('timestamp', required=True)

    def get(self, biometric_id):
        """GET a biometric record by ID from the database

        :param int biometric_id: ID of the biometric to search for.
        :return: JSON reponse object containing a biometric
        """
        record = None
        with open_session() as session:
            try:
                record = session.query(Biometric) \
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
        """PUT a new record into the database
        :param int biometric_id:    Unused for PUT requests
        :returns: JSON response object containing the new ID for the uploaded biometric.
        """
        args = self.parser.parse_args()

        # Convert data_time and validate
        timestamp = utils.str2date(args.timestamp)
        if timestamp is None:
            abort(500)

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
                                  timestamp
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
    """API handler for returning lists of biometric records for a specific patient: /biometrics

    GET: Returns a JSON response containing a complete list of all patients
    """
    parser = reqparse.RequestParser()
    parser.add_argument('patient_id', required=True)
    parser.add_argument('biometric_type_id', required=False)

    def get(self):
        """
        Fetchs the list of biometric records from the database for this patient
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
                logger.info("No record found")
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


class ECGAPI(Resource):
    """API handler for returning ECG data for a specific patient: /ecg"""
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('patient_id', required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('patient_id', required=True)
    put_parser.add_argument('sampling_freq', required=True)
    put_parser.add_argument('sample_count', required=True)
    put_parser.add_argument('timestamp', required=True)
    put_parser.add_argument('data', required=True)

    def get(self):
        """
        Fetchs the list of biometric records from the database for this patient
        :return: JSON encoded list of patient records
        """
        args = self.get_parser.parse_args(strict=True)

        with open_session() as session:
            try:
                records = session.query(ECG.id, ECG.patient_id,
                    ECG.sample_count, ECG.sampling_freq, ECG.timestamp) \
                    .filter(ECG.patient_id == args.patient_id) \
                    .all()
            except NoResultFound:
                logger.info("No record found")
                return gen_response("No result found")
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            # Build the response list
            rlist = [to_dict(record) for record in records]
            return gen_response(rlist)

    def put(self):
        """PUT a new record into the database
        """
        args = self.put_parser.parse_args()

        # Convert data_time and validate
        timestamp = utils.str2date(args.timestamp)
        if timestamp is None:
            abort(500)

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

            # Add ecg record
            ecg = patient.add_ecg(session,
                                  args.sampling_freq,
                                  args.sample_count,
                                  timestamp,
                                  args.data
                )

            if ecg is None:
                logger.warn("PUT: No Patient matching id for biometric")
                return gen_response("No matching Biometric type")

            session.commit()
            return gen_response({"id": ecg.id})

    @staticmethod
    def add(api):
        api.add_resource(ECGAPI, '/ecg')


class ECGDataAPI(Resource):
    """API handler for returning ECG data for a ECG entry: /ecgdata
    
    Response format:
    {
        "response": {
            "header": {
                "id": <int>
                "patient_id": <int>
                "sampling_freq": <float>
                "sample_count": <int>
                "timestamp": <datatime>
            }
            "data": [
                X,X,X,X,X,X,X,X,X
            ]
        }
    }
    """
    parser = reqparse.RequestParser()
    parser.add_argument('id', required=True)

    def get(self):
        """
        Fetchs the ECG data for a specific entry from disk
        :return: JSON encoded ECG records
        """
        args = self.parser.parse_args(strict=True)

        with open_session() as session:
            try:
                db_record = query = session.query(ECG) \
                    .filter(ECG.id == args.id).one()
            except NoResultFound:
                logger.info("No record found")    # TODO: remove debugging
                return gen_response("No result found")
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            record = {
                "header": to_dict(db_record),
                "data" : []
            }

            with open(record['path']) as ecg_file:
                record['data']
                

            return gen_response()

    @staticmethod
    def add(api):
        api.add_resource(ECGDataAPI, '/ecgdata')
    

# Load the api
def load_api(app):
    api = Api(app)
    for resource in Resource.__subclasses__():
        resource.add(api)


# Load the API
load_api(webapp)
