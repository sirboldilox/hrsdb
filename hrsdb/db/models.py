"""
Database implementation
"""
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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

def create_all(engine=None):
    """Create all database tables"""
    if engine is None:
        from hrsdb.db import engine
    Base.metadata.create_all(engine)
