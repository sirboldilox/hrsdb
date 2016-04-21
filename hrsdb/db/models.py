"""
Database implementation
"""
import pickle

from sqlalchemy import BLOB, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class Patient(Base):
    """Patient record table.

    Store general information on patients that can be used to
    filter queries when searching for a particular patient.

    :param int      id:             Uniquie identifier for the patient
    :param str      first_name:     First name of the patient
    :param str      last_name:      Last name of the patient
    :param str      gender:         Gender of the patient - Male(0) Female(1)
    :param datetime date_of_birth:  Date of birth of the patient
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
        """Add a new biometric for this patient
        
        :param session:             Open database session
        :param int type_id:         BiometricType id of the biometric
        :param str value:           Biometric raw value
        :param datetime timestamp:  Timestamp of when the biometric was recorded
        """
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
        """Add a new ECG record for this patient

        :param session:             Open database session
        :param float sampling_freq: Frequency the samples were taken at.
        :param datetime timestamp:  Timestamp of when the biometric was recorded
        :param data:                ECGData object
        """
        ecg = ECG(self.id, sampling_freq, timestamp, data)
        session.add(ecg)
        session.flush()

        return ecg
        

class BiometricType(Base):
    """ Biometric data types

    Static table to store different biometric types

    :param int id:      Uniquie identifier for the patient
    :param str name:    Unique name for this biometric
    :param str units:   Measurement units for this biometric
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
        """Populate this table with static data

        :param session: Open database session
        """

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

    :param int id:              Unique identifier
    :param int patient_id:      ID of the patient the reading belongs to.
    :param int type_id:         ID of the type of biometric reading
    :param str value:           Biometric raw value
    :param datetime timestamp:  Timestamp of when the biometric was recorded
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
    Actually ECG readings will be stored on disk and mapped via the ECGData table

    :param int id:              Unique identifier
    :param int patient_id:      ID of the patient the reading belongs to
    :param float sampling_freq: Frequency the samples were taken at.
    :param int data_id:         ID of the ECGData object this reading relates to
    :param datetime timestamp:  Timestamp of when the biometric was recorded
    """
    __tablename__ = "ecg"

    id            = Column(Integer, primary_key=True)
    patient_id    = Column(ForeignKey("patients.id"))
    sampling_freq = Column(Float)
    data_id       = Column(ForeignKey("ecg_data.id"))
    timestamp     = Column(DateTime)

    data = relationship("ECGData", back_populates="info")

    def __init__(self, patient_id, sampling_freq, data, timestamp):
        self.patient_id = patient_id
        self.sampling_freq = sampling_freq
        self.timestamp = timestamp
        self.data_id = data.id

    def __repr__(self):
        return "<ECG[%d]: P:%d F: %f T: %s>" % (
            self.id,
            self.patient_id,
            self.sampling_freq,
            self.timestamp
        )

class ECGData(Base):
    """ ECG Data records table

    Stores references to actual ECG readings on disk

    :param int id:      Unique identifier
    :param str path:    Full path to the data file on disk
    """
    __tablename__ = "ecg_data"

    id   = Column(Integer, primary_key=True)
    path = Column(String)

    info = relationship("ECG", uselist=False, back_populates="data")

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return "<ECG[%d]: %s>" % (
            self.id,
            self.path
        )
