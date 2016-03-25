"""
Database implementation
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class Patient(Base):
    """Patient record table.

    Store general information on patients that can be used to
    filter queries when searching for a particular patient.

    :param id:              Uniquie identifier for the patient
    :param first_name:      First name of the patient
    :param last_name:       Last name of the patient
    :param gender:          Gender of the patient - Male(0) Female(1)
    :param date_of_birth:   Date of birth of the patient
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String, index=True)
    gender = Column(Integer)
    date_of_birth = Column(DateTime)

    def __init__(self, first_name, last_name, gender, date_of_birth):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.date_of_birth = date_of_birth

    def __repr__(self):
        return "<Patient[%d]: %s %s %s %s> " % (
            self.id,
            self.first_name,
            self.last_name,
            'F' if self.gender else 'M',
            str(self.date_of_birth)
        )

    def add_biometric(self, session, type_id, value, timestamp):
        """Add a new biometric for this patient"""
        try:
            session.query(BiometricType)\
                .filter(BiometricType.id == type_id).one_or_none()
        except NoResultFound:
            return None

        biometric = Biometric(self.id, type_id, value, timestamp)
        session.add(biometric)
        session.flush()

        return biometric


class BiometricType(Base):
    """ Biometric data types

    Static table to store different biometric types

    :param str name: Type name
    """
    __tablename__ = "biometric_types"

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return "<BiometricType: %s>" % self.type


class Biometric(Base):
    """ Biometric data table

    Stores biometric readings from a single patient

    :param int patient_id: ID of the patient the reading belongs to.
    :param type_id: ID of the type of biometric reading
    :param value: The biometric data
    """
    __tablename__ = "biometrics"

    id = Column(Integer, primary_key=True)
    patient_id = Column(ForeignKey("patients.id"))
    type_id = Column(ForeignKey("biometric_types.id"))
    value = Column(String)
    timestamp = Column(DateTime)

    def __init__(self, patient_id, type_id, value, timestamp):
        self.patient_id = patient_id
        self.type_id = type_id
        self.value = value
        self.timestamp = timestamp

    def __repr__(self):
        return "<Biometric[%d]: P:%d T:%d V:%s" % (
            self.id,
            self.patient_id,
            self.type_id,
            self.value
        )

