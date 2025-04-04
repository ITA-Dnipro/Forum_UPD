import pytest
from httpx import AsyncClient
from app.schemas.tag import TagResponse
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch
import json
from typing import List

@pytest.mark.asyncio
async def test_create_tag(client, mock_cassandra_session):
    """Test creating a new tag."""

    tag_data = {
        "name": "Python",
        "description": "Python programming language related posts"
    }
    
    mock_existing = MagicMock()
    mock_existing.one.return_value = None
    
    session_mock = MagicMock()

    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT tag_id FROM tags WHERE name" in query_str:
            return mock_existing
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post("/api/tags/", json=tag_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Python"
        assert result["description"] == "Python programming language related posts"
        assert result["posts_count"] == 0
        assert "tag_id" in result
        assert "created_at" in result

@pytest.mark.asyncio
async def test_create_tag_already_exists(client, mock_cassandra_session):
    """Test creating a tag that already exists."""

    tag_data = {
        "name": "Python",
        "description": "Python programming language related posts"
    }
    
    existing_id = uuid4()
    mock_existing = MagicMock()
    mock_existing.one.return_value = MagicMock(tag_id=existing_id)
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT tag_id FROM tags WHERE name" in query_str:
            return mock_existing
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post("/api/tags/", json=tag_data)
        
        assert response.status_code == 400
        result = response.json()
        assert "already exists" in result["detail"]

@pytest.mark.asyncio
async def test_get_tag(client, mock_cassandra_session):
    """Test retrieving a tag by ID."""
    tag_id = uuid4()
    
    mock_tag = MagicMock()
    mock_tag.tag_id = tag_id
    mock_tag.name = "Python"
    mock_tag.description = "Python programming language related posts"
    mock_tag.posts_count = 8
    mock_tag.created_at = datetime.utcnow()
    mock_tag.updated_at = None
    
    mock_tag._asdict.return_value = {
        "tag_id": tag_id,
        "name": "Python",
        "description": "Python programming language related posts",
        "posts_count": 8,
        "created_at": mock_tag.created_at,
        "updated_at": None
    }
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.one.return_value = mock_tag
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/tags/{tag_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["tag_id"] == str(tag_id)
        assert result["name"] == "Python"
        assert result["description"] == "Python programming language related posts"
        assert result["posts_count"] == 8

@pytest.mark.asyncio
async def test_get_tag_not_found(client, mock_cassandra_session):
    """Test retrieving a non-existent tag."""
    tag_id = uuid4()
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.one.return_value = None
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
       
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/tags/{tag_id}")
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

@pytest.mark.asyncio
async def test_list_tags(client, mock_cassandra_session):
    """Test listing all tags."""

    tag1_id = uuid4()
    tag2_id = uuid4()
    
    mock_tag1 = MagicMock()
    mock_tag1.tag_id = tag1_id
    mock_tag1.name = "Python"
    mock_tag1.description = "Python programming language related posts"
    mock_tag1.posts_count = 8
    mock_tag1.created_at = datetime.utcnow()
    mock_tag1.updated_at = None
    mock_tag1._asdict.return_value = {
        "tag_id": tag1_id,
        "name": "Python",
        "description": "Python programming language related posts",
        "posts_count": 8,
        "created_at": mock_tag1.created_at,
        "updated_at": None
    }
    
    mock_tag2 = MagicMock()
    mock_tag2.tag_id = tag2_id
    mock_tag2.name = "FastAPI"
    mock_tag2.description = "FastAPI framework related posts"
    mock_tag2.posts_count = 5
    mock_tag2.created_at = datetime.utcnow()
    mock_tag2.updated_at = None
    mock_tag2._asdict.return_value = {
        "tag_id": tag2_id,
        "name": "FastAPI",
        "description": "FastAPI framework related posts",
        "posts_count": 5,
        "created_at": mock_tag2.created_at,
        "updated_at": None
    }
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_tag1, mock_tag2]
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get("/api/tags/")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2
        assert result[0]["name"] == "Python"
        assert result[1]["name"] == "FastAPI"

@pytest.mark.asyncio
async def test_update_tag(client, mock_cassandra_session):
    """Test updating a tag."""
    tag_id = uuid4()
    
    update_data = {
        "name": "Updated Python",
        "description": "Updated description for Python"
    }
    
    mock_existing = MagicMock()
    mock_existing.tag_id = tag_id
    mock_existing.name = "Python"
    mock_existing.description = "Original description"
    mock_existing.posts_count = 8
    mock_existing.created_at = datetime.utcnow()
    mock_existing.updated_at = None
    
    mock_updated = MagicMock()
    mock_updated.tag_id = tag_id
    mock_updated.name = "Updated Python"
    mock_updated.description = "Updated description for Python"
    mock_updated.posts_count = 8
    mock_updated.created_at = mock_existing.created_at
    mock_updated.updated_at = datetime.utcnow()
    mock_updated._asdict.return_value = {
        "tag_id": tag_id,
        "name": "Updated Python",
        "description": "Updated description for Python",
        "posts_count": 8,
        "created_at": mock_existing.created_at,
        "updated_at": mock_updated.updated_at
    }
    
    session_mock = MagicMock()
    
    existing_result = MagicMock()
    existing_result.one.return_value = mock_existing
    
    updated_result = MagicMock()
    updated_result.one.return_value = mock_updated
    
    session_mock.execute.side_effect = [
        existing_result,  
        MagicMock(),      
        updated_result    
    ]
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.put(f"/api/tags/{tag_id}", json=update_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["tag_id"] == str(tag_id)
        assert result["name"] == "Updated Python"
        assert result["description"] == "Updated description for Python"
        assert "updated_at" in result

@pytest.mark.asyncio
async def test_update_tag_not_found(client, mock_cassandra_session):
    """Test updating a non-existent tag."""
    tag_id = uuid4()
    
    update_data = {
        "name": "Updated Python",
        "description": "Updated description"
    }
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.one.return_value = None
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.put(f"/api/tags/{tag_id}", json=update_data)
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

@pytest.mark.asyncio
async def test_delete_tag(client, mock_cassandra_session):
    """Test deleting a tag."""
    tag_id = uuid4()
    
    session_mock = MagicMock()
    
    existing_result = MagicMock()
    existing_result.one.return_value = MagicMock(tag_id=tag_id)
    
    session_mock.execute.side_effect = [
        existing_result,  
        MagicMock()       
    ]
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.delete(f"/api/tags/{tag_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["tag_id"] == str(tag_id)
        assert "Tag deleted" in result["message"]

@pytest.mark.asyncio
async def test_delete_tag_not_found(client, mock_cassandra_session):
    """Test deleting a non-existent tag."""
    tag_id = uuid4()
    
    session_mock = MagicMock()
    
    existing_result = MagicMock()
    existing_result.one.return_value = None
    
    session_mock.execute.return_value = existing_result
    
    with patch("app.routes.tags.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.delete(f"/api/tags/{tag_id}")
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]