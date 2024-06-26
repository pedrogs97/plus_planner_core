"""Project Enums"""

from enum import Enum


class MessageType(Enum):
    """Message Type Enum"""

    NEW_PATIENT_IN_WAIT = 1
    UPDATE_PATIENT_IN_WAIT = 2
    NEXT_PATIENT_IN_WAIT = 3
    LIST_PATIENTS_IN_WAIT = 4
    CONNECTION = 5
    CREATE_UUID = 6
    INVALID = 7
    ERROR = 8
    DISCONNECT = 9
