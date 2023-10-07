from enum import Enum


class Apply(Enum):
    PENDING = 'pending'
    CANCEL = 'cancel'
    CONFIRM = 'confirm'


PATHS = {
    "company": "companies",
    "teacher": "teachers",
}

# the amount of prefetch items from match data
PREFETCH = 3

BRIEF_JOB_SIZE = 20

# serial_key is a field of the collection in the user's cache
SERIAL_KEY = "created_at"
