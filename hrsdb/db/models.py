"""
Database implementation
"""
import pickle

from sqlalchemy import BLOB, Column, DateTime, Float, ForeignKey, Integer, String
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
        return "<Patient[%d]: %s %s %s %s>" % (
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

    def add_ecg(self, session, sampling_freq, timestamp, data):
        """Add a new ECG record for this patient"""
        ecg = ECG(self.id, sampling_freq, timestamp, data)
        session.add(ecg)
        session.flush()

        return ecg
        

class BiometricType(Base):
    """ Biometric data types

    Static table to store different biometric types

    :param str name: Type name
    """
    static_data = [
        (1, "height", "cm"),
        (2, "weight", "kg"),
        (3, "blood pressure", "mm Hg"),
        (10, "ecg", "mV")
    ]

    __tablename__ = "biometric_types"

    id   = Column(Integer, primary_key=True)
    name = Column(String)
    units = Column(String)

    def __init__(self, id, name, units):
        self.id = id
        self.name = name
        self.units = units

    def __repr__(self):
        return "<BiometricType: %s %s>" % (self.name, self.units)

    @staticmethod
    def create_static(session):
        """Populate this table with static data"""

        local_data = session.query(BiometricType).all()
        for id, name, units in BiometricType.static_data:
            present = False
            for entry in local_data:
                if entry.name == name:
                    present = True
                    break

            # Add missing entries
            if not present:
                session.add(BiometricType(id, name, units))


class Biometric(Base):
    """ Biometric data table

    Stores biometric readings from a single patient

    :param int patient_id: ID of the patient the reading belongs to.
    :param type_id: ID of the type of biometric reading
    :param value: The biometric data
    """
    __tablename__ = "biometrics"

    id         = Column(Integer, primary_key=True)
    patient_id = Column(ForeignKey("patients.id"))
    type_id    = Column(ForeignKey("biometric_types.id"))
    value      = Column(String)
    timestamp  = Column(DateTime)

    def __init__(self, patient_id, type_id, value, timestamp):
        self.patient_id = patient_id
        self.type_id = type_id
        self.value = value
        self.timestamp = timestamp

    def __repr__(self):
        return "<Biometric[%d]: P:%d T:%d V:%s>" % (
            self.id,
            self.patient_id,
            self.type_id,
            self.value
        )


class ECG(Base):
    """ ECG record table

    Stores basic information about ECG's stored.
    Actually ECG readings will be stored on disk
    """
    __tablename__ = "ecg"

    id            = Column(Integer, primary_key=True)
    patient_id    = Column(ForeignKey("patients.id"))
    sampling_freq = Column(Float)
    sample_count  = Column(Integer)
    timestamp     = Column(DateTime)
    data          = Column(BLOB)

    def __init__(self, patient_id, sampling_freq, timestamp, data):
        self.patient_id = patient_id
        self.sampling_freq = sampling_freq
        self.sample_count = len(data)
        self.timestamp = timestamp
        self.data = self.encode(data)

    def __repr__(self):
        return "<ECG[%d]: P:%d F: %f L: %d T: %s>" % (
            self.id,
            self.patient_id,
            self.sampling_freq,
            self.sample_count,
            self.timestamp
        )

    def encode(self, data):
        """Encode readings to be stored in database"""
        self.data = pickle.dumps(data)

    def decode(self):
        """Decode readings from database to array"""
        return pickle.loads(self.data)
