import asyncio

from dotenv import load_dotenv
from elasticsearch import ConnectionError
from elasticsearch_dsl import async_connections

from ..config import settings, logger

load_dotenv()


async def elasticsearch_init():
    """Establishes a connection to Elasticsearch with retries."""
    elasticsearch_host = settings.ELASTICSEARCH_HOST
    retry = settings.ELASTICSEARCH_MAX_RETRIES
    delay = settings.ELASTICSEARCH_RETRY_DELAY

    for attempt in range(retry):
        try:
            async_connections.create_connection(hosts=[elasticsearch_host], alias="default")
            es = async_connections.get_connection()

            if await es.ping():
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
