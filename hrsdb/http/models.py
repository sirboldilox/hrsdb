"""
Record type definitions for the HTTP API
"""
from flask import jsonify
from flask_restful import Api, Resource
from sqlalchemy.orm.exc import NoResultFound

# Local imports
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

    def get(self, patient_id):
        """GET a patient record by ID from the database"""
        print(patient_id)

        record = None
        with DBHandler() as db_han:
            try:
                print(db_han.session.query(Patient).all())
            except:
                print("Exception in test run")
            try:
                record = db_han.session.query(Patient)\
                    .filter(Patient.id == patient_id).one()
            except NoResultFound:
                print("No record found")
                return jsonify({})
            except Exception as error:
                print("Exeption: %s" % (str(error)))
                return jsonify({})

        print(record)
        return jsonify(**to_dict(record))

    @staticmethod
    def add(api):
        api.add_resource(PatientAPI, '/patient/<int:patient_id>')


# Load the api
def load_api(app):
    api = Api(app)
    print("* Loading API:")
    for resource in Resource.__subclasses__():
        print("  -> %s" % (resource.__name__))
        resource.add(api)
