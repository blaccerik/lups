# Set the logging level to INFO
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('gunicorn')
logger.info("log works")