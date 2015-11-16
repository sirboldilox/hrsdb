"""
General database settings
"""
from sqlalchemy import create_engine

db_url = 'sqlite:///hrs_test.db'
engine = create_engine(db_url)

