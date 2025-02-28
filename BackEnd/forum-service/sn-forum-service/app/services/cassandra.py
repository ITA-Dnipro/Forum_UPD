# app/services/cassandra.py
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import time
import asyncio
from app.config import settings 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_session = None
_session_lock = asyncio.Lock()

async def get_session():
    global _session
    async with _session_lock: 
        if _session is None:
            _session = await async_init_cassandra()
        return _session

async def async_init_cassandra():
    auth_provider = PlainTextAuthProvider(
        username=settings.cassandra_username,
        password=settings.cassandra_password
    )
    
    max_retries = settings.cassandra_max_retries
    retry_delay = settings.cassandra_retry_delay
    
    for attempt in range(max_retries):
        try:
            cluster = Cluster(
                settings.cassandra_contact_points,
                port=settings.cassandra_port,
                auth_provider=auth_provider,
                protocol_version=5
            )
            
            session = cluster.connect()
            
            session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {settings.cassandra_keyspace}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
            """)
            
            session.set_keyspace(settings.cassandra_keyspace)
            
            await register_user_types(cluster)
            
            logger.info(f"Successfully connected to Cassandra and set keyspace to {settings.cassandra_keyspace}")
            return session
            
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to Cassandra after {max_retries} attempts: {str(e)}")
                raise
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay) 

async def register_user_types(cluster):
    
    try:
        cluster.register_user_type(settings.cassandra_keyspace, "category_info", dict)
        cluster.register_user_type(settings.cassandra_keyspace, "tag_info", dict)
        logger.info("User types registered successfully")
    except Exception as e:
        logger.error(f"Failed to register user types: {str(e)}")
        raise