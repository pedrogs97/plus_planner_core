"""Project Enums"""

from enum import Enum


class WaitListMessageType(Enum):
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


class Ufs(str, Enum):
    """Brazil ufs"""

    AC = "AC"
    AL = "AL"
    AP = "AP"
    AM = "AM"
    BA = "BA"
    CE = "CE"
    DF = "DF"
    ES = "ES"
    GO = "GO"
    MA = "MA"
    MT = "MT"
    MS = "MS"
    MG = "MG"
    PA = "PA"
    PB = "PB"
    PR = "PR"
    PE = "PE"
    PI = "PI"
    RJ = "RJ"
    RN = "RN"
    RS = "RS"
    RO = "RO"
    RR = "RR"
    SC = "SC"
    SP = "SP"
    SE = "SE"
    TO = "TO"


class SchedulerMessageType(int, Enum):
    """Message Type Enum"""

    GET_FULL_MONTH_CALENDAR = 1
    GET_FULL_WEEK_CALENDAR = 2
    GET_DAY_CALENDAR = 3
    ADD_EVENT = 4
    EDIT_EVENT = 5
    REMOVE_EVENT = 6
    CONNECTION = 7
    CREATE_UUID = 8
    INVALID = 9
    ERROR = 10
    DISCONNECT = 11
