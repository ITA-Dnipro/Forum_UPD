import pytest
from fastapi.testclient import TestClient
from app.main import app
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from cassandra.query import SimpleStatement

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def mock_cassandra_session(mocker):
    
    mock_session = MagicMock()
    
    configured_queries = {}
    
    def handle_execute(query, *args, **kwargs):
        """Custom execute handler that tracks the queries"""
        
        query_str = query.query_string if isinstance(query, SimpleStatement) else query
        
        print(f"QUERY: {query_str}")
        print(f"ARGS: {args}")
        
        if query_str in configured_queries:
            result, method = configured_queries[query_str]
            if method == 'direct':
                return result
            elif method == 'one':
                result_mock = MagicMock()
                result_mock.one.return_value = result
                return result_mock
            elif method == 'all':
                result_mock = MagicMock()
                result_mock.all.return_value = result
                return result_mock
        
        for pattern, (result, method) in configured_queries.items():
            if pattern in query_str:
                if method == 'direct':
                    return result
                elif method == 'one':
                    result_mock = MagicMock()
                    result_mock.one.return_value = result
                    return result_mock
                elif method == 'all':
                    result_mock = MagicMock()
                    result_mock.all.return_value = result
                    return result_mock
        
        default_mock = MagicMock()
        default_mock.one.return_value = None
        default_mock.all.return_value = []
        default_mock.paging_state = None
        return default_mock
    
    def configure_execute(query_pattern, result, method='direct'):
        """Store a query pattern and its expected result"""
        configured_queries[query_pattern] = (result, method)
        print(f"Configured: {query_pattern} -> {result} ({method})")
    
    mock_session.execute = handle_execute
    mock_session.configure_execute = configure_execute
    
    mocker.patch("app.services.cassandra.async_init_cassandra", return_value=mock_session)
    mocker.patch("app.services.cassandra.get_session", return_value=mock_session)
    
    stmt_mock = mocker.patch("cassandra.query.SimpleStatement")
    stmt_mock.side_effect = lambda query, **kwargs: MagicMock(query_string=query)
    
    return mock_session

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()