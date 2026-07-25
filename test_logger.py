from deriv_sdk.logger import configure_logger, get_logger

configure_logger()

logger = get_logger(__name__)

logger.info("SDK started")
logger.warning("This is a warning")
logger.error("This is an error")
