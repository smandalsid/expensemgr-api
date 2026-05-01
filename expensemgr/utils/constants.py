from enum import Enum

auth_failed = "Authentication Failed!"


class DivisionBy(Enum):
    AMOUNT = "AMOUNT"
    PERCENTAGE = "PERCENTAGE"


class VersionActiveInd(Enum):
    ACTIVE = True
    INACTIVE = False


class DeleteInd(Enum):
    YES = True
    NO = False

class ExpenseVerStatus(Enum):
    PAID = True
    DUE = False