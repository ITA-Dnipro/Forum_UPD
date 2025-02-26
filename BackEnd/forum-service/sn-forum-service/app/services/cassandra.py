# app/services/cassandra.py
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import time
from app.config import settings 

_session = None

def get_session():
    global _session
    if _session is None:
        _session = init_cassandra()
    return _session

def init_cassandra(): 
    
    auth_provider = PlainTextAuthProvider(
        username=settings.cassandra_username,
        password=settings.cassandra_password
    )
    
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            cluster = Cluster(
                [settings.cassandra_host],
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
            
            cluster.register_user_type(settings.cassandra_keyspace, "category_info", dict)
            cluster.register_user_type(settings.cassandra_keyspace, "tag_info", dict)
            
            print(f"Successfully connected to Cassandra and set keyspace to {settings.cassandra_keyspace}")
            return session
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to connect to Cassandra after {max_retries} attempts: {str(e)}")
                raise
            print(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

