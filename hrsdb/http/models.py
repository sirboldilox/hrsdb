"""
Record type definitions for the HTTP API
"""
from flask import jsonify, abort
from flask_restful import Api, Resource, reqparse
from sqlalchemy.orm.exc import NoResultFound

# Local imports
from hrsdb import utils
from hrsdb.db import DBHandler, to_dict
from hrsdb.db.models import Patient


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
        """GET a patient record by ID from the database"""
        if patient_id is not None:
            print(patient_id)
        else:
            print("No patient ID")
            return

        with DBHandler() as db_han:
            try:
                record = db_han.query(Patient) \
                    .filter(Patient.id == patient_id).one()
            except NoResultFound:
                print("No record found")    # TODO: remove debugging
                return jsonify({})
            except Exception as error:
                print("Exeption: %s" % (str(error)))
                return jsonify({})

            response = {
                "response": to_dict(record)
            }

            return jsonify(response)

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
            return jsonify({"response": "error"})
        else:
            return jsonify({"response": {"id": return_id}})

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
                return jsonify({})
            except Exception as error:
                print("Exeption: %s" % (str(error)))
                return jsonify({})

            # Build the response list
            rlist = [to_dict(record) for record in records]
            response = {
                "response": rlist
            }
            return jsonify(response)

    @staticmethod
    def add(api):
        api.add_resource(PatientListAPI, '/patient')


# Load the api
def load_api(app):
    api = Api(app)
    print("* Loading API:")
    for resource in Resource.__subclasses__():
        print("  -> %s" % (resource.__name__))
        resource.add(api)
