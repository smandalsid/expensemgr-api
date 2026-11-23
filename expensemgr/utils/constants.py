from enum import Enum, IntEnum

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


class ExpenseStatus(Enum):
    SETTLED = True
    DUE = False


class ConnectionConsent(Enum):
    YES = True
    NO = False


class ExpenseOrderBy(IntEnum):
    EXPENSE_DT = 0
    LAST_UPDATED = 1
