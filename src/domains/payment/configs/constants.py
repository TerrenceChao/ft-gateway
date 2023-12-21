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
    PaymentStatusEnum.PROCESSING.value,
    PaymentStatusEnum.PAID.value,
}
UNABLE_TO_SUBSCRIBE = {
    PaymentStatusEnum.PROCESSING.value,
    PaymentStatusEnum.PAID.value,
    PaymentStatusEnum.CANCELING.value,
}
UNABLE_TO_CANCEL_SUBSCRIBE = {
    PaymentStatusEnum.PROCESSING.value,
    PaymentStatusEnum.UNPAID.value,
    PaymentStatusEnum.CANCELING.value,
    PaymentStatusEnum.CANCELED.value,
}
SECONDS_OF_DAY = 86400
