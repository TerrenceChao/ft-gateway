from enum import Enum


# merchant
STRIPE = 'stripe'

# payment type
LONG_TERM_SUBSCRIPTION = 'long_term_subscription'

class PaymentStatusEnum(Enum):
    UNPAID = 'unpaid'
    PROCESSING = 'processing'
    PAID = 'paid'
    CANCELING = 'canceling'
    CANCELED = 'canceled'
    
PAYMENT_PERIOD = set([
    PaymentStatusEnum.PROCESSING.value,
    PaymentStatusEnum.PAID.value,
    ])
CANCEL_PERIOD = set([
    PaymentStatusEnum.UNPAID.value,
    PaymentStatusEnum.CANCELING.value, 
    PaymentStatusEnum.CANCELED.value,
    ])
SECONDS_OF_DAY = 86400
