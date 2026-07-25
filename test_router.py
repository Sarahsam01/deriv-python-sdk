from deriv_sdk.logger import configure_logger
from deriv_sdk.transport.router import MessageRouter

configure_logger()

router = MessageRouter()


def tick_handler(message):
    print("Tick Handler:")
    print(message)


def authorize_handler(message):
    print("Authorize Handler:")
    print(message)


router.register(
    "tick",
    tick_handler,
)

router.register(
    "authorize",
    authorize_handler,
)

router.dispatch(
    {
        "msg_type": "tick",
        "tick": {
            "quote": 123.45,
        },
    }
)

router.dispatch(
    {
        "msg_type": "authorize",
        "authorize": {
            "loginid": "VRTC12345",
        },
    }
)

router.dispatch(
    {
        "msg_type": "balance",
    }
)
