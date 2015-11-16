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
    """
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    second_name = Column(String, index=True)
    gender = Column(Integer)
    date_of_birth = Column(DateTime)

def create_all():
    """Create all database tables"""
    from hrsdb.db import engine
    Base.metadata.create_all(engine)
