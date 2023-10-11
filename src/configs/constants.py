from enum import Enum

REGION_MAPPING = {
    'us-east-1': 'us-e1',
    'us-east-2': 'us-e2',
    'us-west-1': 'us-w1',
    'us-west-2': 'us-w2',
    'ca-central-1': 'ca-c1',
    'eu-north-1': 'eu',
    'eu-west-2': 'uk',
    'eu-west-3': 'fr',
    'eu-south-1': 'it',
    'eu-central-1': 'de',
    'ap-northeast-1': 'jp',
    'ap-northeast-2': 'kr',
    'ap-southeast-1': 'sg',
    'ap-southeast-2': 'au',
    'ap-south-1': 'in',
    'sa-east-1': 'br'
}


VALID_ROLES = set(['company', 'teacher'])


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
