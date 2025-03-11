import logging.config
from BackEnd.forum.settings import LOGGING


logging.config.dictConfig(LOGGING)

logger = logging.getLogger("utils_validation_service")

logger.error(f'Test ERROR')
logger.critical(f'Test CRITICAL')
