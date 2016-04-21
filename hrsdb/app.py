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
import csv
import logging
import os
import werkzeug

from flask import Flask, jsonify, abort, current_app
from flask_restful import Api, Resource, reqparse
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4 as uuid

# Local imports
from hrsdb import utils
from hrsdb.db import open_session, to_dict
from hrsdb.db.models import Biometric, BiometricType, ECG, ECGData, Patient

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
    """API handler for accessing patient records: **/patient/<id:int>**"""

    # Parser for PUT requests
    parser = reqparse.RequestParser()
    parser.add_argument('first_name', required=True)
    parser.add_argument('last_name', required=True)
    parser.add_argument('gender', type=int, required=True)
    parser.add_argument('date_of_birth', required=True)

    def get(self, patient_id):
        """Get a patient record by ID from the database

        Example **GET http://hrsdb/patient/1** ::

            {
              "response": {
                "id": 1,
                "first_name": "Bob",
                "last_name": "Smith",
                "gender": 0,
                "date_of_birth": "1997/04/12"
              }
            }
        
        """
        with open_session() as session:
            try:
                record = session.query(Patient) \
                    .filter(Patient.id == patient_id).one()
            except NoResultFound:
                logger.info("No record found")
                resp = gen_response("No record found")
                resp.status_code = 404
                return resp

            except Exception as error:
                print("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            return gen_response(to_dict(record))

    def put(self, patient_id):
        """PUT a new record into the database
        Example JSON Body **PUT http://hrsdb/patient/0** ::

            {
                "first_name": "Bob",
                "last_name": "Smith",
                "gender": 0,
                "date_of_birth": "1997/04/12"
            }

        Example response::

            {
              "response": {
                "id": 1
              }
            }

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
    """API handler for returning lists of patient records: **/patients**"""

    def get(self):
        """Gets all patient records from the database

        Example **GET http://hrsdb/patients**

        .. code-block:: javascript

            {
              "response": [
                {
                  "id": 1,
                  "first_name": "Bob",
                  "last_name": "Smith",
                  "gender": 0,
                  "date_of_birth": "1997/04/12"

                }
                {
                  "id": 2
                  ...
                }
              ]
            }

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
    """API handler for accessing biometric types: **/biometric_types**"""

    def get(self):
        """Get all biometric types from the database

        Example **GET http://hrsdb/biometric_types** ::

            {
              "response": [
                {
                  "id": 1,
                  "name": "height",
                  "units" "cm"
                }
                {
                  "id": 2,
                  "name": "weight",
                  "units": "kg"
                }
                ...
              ]
            }

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
    """API handler for accessing biometric records: **/biometric/<id:int>**"""
    parser = reqparse.RequestParser()
    parser.add_argument('patient_id', required=True)
    parser.add_argument('biometric_type_id', required=True)
    parser.add_argument('value', required=True)
    parser.add_argument('timestamp', required=True)

    def get(self, biometric_id):
        """Get a biometric record by ID from the database

        Example **GET http://hrsdb/biometric/1** ::

            {
              "response": {
                  "id": 1,
                  "patient_id": 1,
                  "timestamp": "2015/05/19" 12:04:59,
                  "type_id": 1,
                  "value": "167"
              }
            }

        """
        record = None
        with open_session() as session:
            try:
                record = session.query(Biometric) \
                    .filter(Biometric.id == biometric_id).one()
            except NoResultFound:
                logger.warn("No record found")
                resp = gen_response("No record found")
                resp.status_code = 404
                return resp
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            logger.debug(record)
            return gen_response(to_dict(record))

    def put(self, biometric_id):
        """Put a new biometric record into the database
        Example JSON Body **PUT http://hrsdb/biometric/0** ::

            {
              "patient_id": 1,
              "timestamp": "2015/05/19" 12:04:59,
              "type_id": 1,
              "value": "167"
            }

        Example response::

            {
              "response": {
                "id": 1
              }
            }

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
    """API handler for returning lists of biometric records for a specific patient: **/biometrics**
    """
    parser = reqparse.RequestParser()
    parser.add_argument('patient_id', required=True)
    parser.add_argument('biometric_type_id', required=False)

    def get(self):
        """
        Fetchs the list of biometric records from the database for this patient
        The list can optionally be filtered using a biometric_type id.

        Example **GET http://hrsdb/biometrics?patient_id=1&biometric_type_id=1**
        
        .. code-block:: javascript

            {
              "response": [
                {
                  "id": 1,
                  "patient_id": 1,
                  "timestamp": "2015/05/19" 12:04:59,
                  "type_id": 1,
                  "value": "167"
                }
                {
                  "id":2,
                  ...
                }
              ]
            }

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
                resp = gen_response("No result found")
                resp.status_code = 404
                return resp
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
    """API handler for returning ECG data for a specific patient: **/ecg**"""
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('patient_id', required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('patient_id', type=int, required=True)
    put_parser.add_argument('sampling_freq', type=float, required=True)
    put_parser.add_argument('data_id', type=int, required=True)
    put_parser.add_argument('timestamp', required=True)

    def get(self):
        """
        Fetchs a list of ecgc records from the database for a specific patient.
        Example **GET http://hrsdb/ecg?patient_id=1**
        
        .. code-block:: javascript

            {
              "response": [
                {
                  "id": 1,
                  "patient_id": 1,
                  "sampling_freq": 1000.0
                  "timestamp": "2015/05/19" 12:04:59,
                  "data_id": 1,
                }
                {
                  "id":2,
                  ...
                }
              ]
            }

        """
        args = self.get_parser.parse_args(strict=True)

        with open_session() as session:
            try:
                records = session.query(ECG) \
                    .filter(ECG.patient_id == args.patient_id) \
                    .all()
            except NoResultFound:
                logger.info("No record found")
                resp = gen_response("No result found")
                resp.status_code = 404
                return resp
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            # Build the response list
            print(records)
            rlist = [to_dict(record) for record in records]
            return gen_response(rlist)

    def put(self):
        """Put a new ECG record into the database
        Example JSON Body **PUT http://hrsdb/ecg** ::

            {
              "id": 1,
              "patient_id": 1,
              "sampling_freq": 1000.0
              "timestamp": "2015/05/19" 12:04:59,
              "data_id": 1,
            }

        Example response::

            {
              "response": {
                "id": 1
              }
            }

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

                ecgdata = session.query(ECGData) \
                            .filter(ECGData.id == args.data_id).one()
            except NoResultFound:
                logger.warn("PUT: No Patient matching id for biometric")
                return gen_response("No matching Patient")
            except Exception as error:
                logger.exception("Exception: %s" % (str(error)))
                return gen_response("Internal server error")

            # Add ecg record
            ecg = patient.add_ecg(
                session,
                args.sampling_freq,
                ecgdata,
                timestamp
            )

            session.commit()
            return gen_response({"id": ecg.id})

    @staticmethod
    def add(api):
        api.add_resource(ECGAPI, '/ecg')


class ECGDataAPI(Resource):
    """API handler for returning ECG data for a ECG entry: **/ecgdata**"""
    file_prefix = 'ecg_'

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('id', required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument(
        'data',
        type=werkzeug.datastructures.FileStorage,
        location='files',
        required=True
    )

    def get(self):
        """
        Fetchs the ECG data for a specific entry from disk
        Example **GET http://hrsdb/ecgdata?id=1**
        
        .. code-block:: javascript

            {
              "response": [
                 0,0,0,0,10,40...
              ]
            }
        """
        args = self.get_parser.parse_args(strict=True)

        with open_session() as session:
            try:
                db_record = query = session.query(ECGData) \
                    .filter(ECGData.id == args.id).one()
            except NoResultFound:
                logger.info("No record found")    # TODO: remove debugging
                resp = gen_response("No result found")
                resp.status_code = 404
                return resp
            except Exception as error:
                logger.exception("Exeption: %s" % (str(error)))
                return gen_response("Internal server error")

            data_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], db_record.path)
            with open(data_file_path) as data_file:
                csv_reader = csv.reader(data_file)
                data = list(csv_reader)[0]

            return gen_response(data)

    def put(self):
        """ Upload an ECG datafile to the server.
        The file should be labled as "data" when uploaded

        Example URL **PUT http://hrsdb/ecgdata**

        Example response::

            {
              "response": {
                "id": 1
              }
            }
        """

        args = self.put_parser.parse_args(strict=True)
        ecgfile = args.data

        # Save the file on disk using a uuid
        filename = "%s%s.dat" % (self.file_prefix, uuid())
        ecgfile.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        # Create a new database record for this file
        with open_session() as session:
            ecgdata = ECGData(filename)
            session.add(ecgdata)
            session.flush()
            session.commit()

            print(ecgdata.id)

            return gen_response({"id": ecgdata.id})

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
