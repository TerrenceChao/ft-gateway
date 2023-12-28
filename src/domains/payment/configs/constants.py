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


PAYMENT_PERIOD = {
    PaymentStatusEnum.PROCESSING,
    PaymentStatusEnum.PAID,
}
UNABLE_TO_SUBSCRIBE = {
    PaymentStatusEnum.PROCESSING,
    PaymentStatusEnum.PAID,
    PaymentStatusEnum.CANCELING,
}
UNABLE_TO_CANCEL_SUBSCRIBE = {
    PaymentStatusEnum.PROCESSING,
    PaymentStatusEnum.UNPAID,
    PaymentStatusEnum.CANCELING,
    PaymentStatusEnum.CANCELED,
}
SECONDS_OF_DAY = 86400
