"""Clinic office repository"""

from plus_db_agent.models import PatientModel
from plus_db_agent.repository import GenericRepository


class PatientRepository(GenericRepository):
    """Patient repository class that will be inherited by all other repositories"""

    def __init__(self):
        self.model = PatientModel
