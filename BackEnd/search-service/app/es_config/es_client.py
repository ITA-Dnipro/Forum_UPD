import asyncio
import logging

from dotenv import load_dotenv
from elasticsearch import ConnectionError
from elasticsearch_dsl import connections

from ..config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("elastic_transport").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

load_dotenv()


async def elasticsearch_init():
    """Establishes a connection to Elasticsearch with retries."""
    elasticsearch_host = settings.elasticsearch_host
    retry = settings.elasticsearch_max_retries
    delay = settings.elasticsearch_retry_delay

    for attempt in range(retry):
        try:
            connections.create_connection(hosts=[elasticsearch_host])
            es = connections.get_connection()

            if es.ping():
                logger.info("Elasticsearch connection is stable.")
                return es
            else:
                raise ConnectionError("Elasticsearch connection is absent.")

        except ConnectionError as e:
            if attempt == retry - 1:
                logger.error(f"All retry attempts failed for Elasticsearch: {str(e)}")
                raise

            logger.warning(
                f"Attempt {attempt + 1}/{retry}: Elasticsearch connection failed, retrying in {delay} seconds...")

            await asyncio.sleep(delay)
