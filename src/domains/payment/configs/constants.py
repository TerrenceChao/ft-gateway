from enum import Enum


# merchant
STRIPE = 'stripe'

# payment type
LONG_TERM_SUBSCRIPTION = 'long_term_subscription'


class PaymentStatusEnum(Enum):
    TRIALING = 'trialing'
    UNPAID = 'unpaid'
    PROCESSING = 'processing'
    PAID = 'paid'
    CANCELING = 'canceling'
    CANCELED = 'canceled'


PAYMENT_PERIOD = {
    PaymentStatusEnum.PROCESSING,
    PaymentStatusEnum.PAID,
}
SECONDS_OF_DAY = 86400


class SubscribeStatusEnum(Enum):
    SUBSCRIBING = 'subscribing'
    ACTIVE = 'active'
    STOPPING = 'stopping'
    STOPPED = 'stopped'
    NOT_SUBSCRIBED = 'not_subscribed'


SUBSCRIBING = {
    SubscribeStatusEnum.SUBSCRIBING,
    SubscribeStatusEnum.ACTIVE,
    SubscribeStatusEnum.STOPPING,
    SubscribeStatusEnum.STOPPED,
}
UNABLE_TO_SUBSCRIBE = {
    SubscribeStatusEnum.SUBSCRIBING,
    SubscribeStatusEnum.ACTIVE,
}
UNABLE_TO_CANCEL_SUBSCRIBE = {
    SubscribeStatusEnum.STOPPING,
    SubscribeStatusEnum.STOPPED,
    SubscribeStatusEnum.NOT_SUBSCRIBED,
}
