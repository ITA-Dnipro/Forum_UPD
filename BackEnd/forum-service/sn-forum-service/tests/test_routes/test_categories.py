import pytest
from httpx import AsyncClient
from app.schemas.category import CategoryResponse
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch
import json
from typing import List

@pytest.mark.asyncio
async def test_create_category(client, mock_cassandra_session):
    """Test creating a new category."""

    category_data = {
        "name": "Technology",
        "description": "Technology related posts"
    }
    
    mock_existing = MagicMock()
    mock_existing.one.return_value = None
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT category_id FROM categories WHERE name" in query_str:
            return mock_existing
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.categories.get_session", return_value=session_mock):

        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post("/api/categories/", json=category_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Technology"
        assert result["description"] == "Technology related posts"
        assert result["posts_count"] == 0
        assert "category_id" in result
        assert "created_at" in result

@pytest.mark.asyncio
async def test_create_category_already_exists(client, mock_cassandra_session):
    """Test creating a category that already exists."""

    category_data = {
        "name": "Technology",
        "description": "Technology related posts"
    }
    
    existing_id = uuid4()
    mock_existing = MagicMock()
    mock_existing.one.return_value = MagicMock(category_id=existing_id)
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT category_id FROM categories WHERE name" in query_str:
            return mock_existing
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.categories.get_session", return_value=session_mock):

        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post("/api/categories/", json=category_data)
        
        assert response.status_code == 400
        result = response.json()
        assert "already exists" in result["detail"]

@pytest.mark.asyncio
async def test_get_category(client, mock_cassandra_session):
    """Test retrieving a category by ID."""
    category_id = uuid4()
    
    mock_category = MagicMock()
    mock_category.category_id = category_id
    mock_category.name = "Science"
    mock_category.description = "Science related posts"
    mock_category.posts_count = 5
    mock_category.created_at = datetime.utcnow()
    mock_category.updated_at = None
    
    mock_category._asdict.return_value = {
        "category_id": category_id,
        "name": "Science",
        "description": "Science related posts",
        "posts_count": 5,
        "created_at": mock_category.created_at,
        "updated_at": None
    }
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.one.return_value = mock_category
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.categories.get_session", return_value=session_mock):
     
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/categories/{category_id}")

        assert response.status_code == 200
        result = response.json()
        assert result["category_id"] == str(category_id)
        assert result["name"] == "Science"
        assert result["description"] == "Science related posts"
        assert result["posts_count"] == 5

@pytest.mark.asyncio
async def test_get_category_not_found(client, mock_cassandra_session):
    """Test retrieving a non-existent category."""
    category_id = uuid4()
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.one.return_value = None
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.categories.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/categories/{category_id}")
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

@pytest.mark.asyncio
async def test_list_categories(client, mock_cassandra_session):
    """Test listing all categories."""
    
    cat1_id = uuid4()
    cat2_id = uuid4()
    
    mock_category1 = MagicMock()
    mock_category1.category_id = cat1_id
    mock_category1.name = "Science"
    mock_category1.description = "Science related posts"
    mock_category1.posts_count = 5
    mock_category1.created_at = datetime.utcnow()
    mock_category1.updated_at = None
    mock_category1._asdict.return_value = {
        "category_id": cat1_id,
        "name": "Science",
        "description": "Science related posts",
        "posts_count": 5,
        "created_at": mock_category1.created_at,
        "updated_at": None
    }
    
    mock_category2 = MagicMock()
    mock_category2.category_id = cat2_id
    mock_category2.name = "Technology"
    mock_category2.description = "Technology related posts"
    mock_category2.posts_count = 10
    mock_category2.created_at = datetime.utcnow()
    mock_category2.updated_at = None
    mock_category2._asdict.return_value = {
        "category_id": cat2_id,
        "name": "Technology",
        "description": "Technology related posts",
        "posts_count": 10,
        "created_at": mock_category2.created_at,
        "updated_at": None
    }
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_category1, mock_category2]
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.categories.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get("/api/categories/")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 2
        assert result[0]["name"] == "Science"
        assert result[1]["name"] == "Technology"

@pytest.mark.asyncio
async def test_update_category(client, mock_cassandra_session):
    """Test updating a category."""
    category_id = uuid4()
    
    update_data = {
        "name": "Updated Science",
        "description": "Updated description"
    }
    
    mock_existing = MagicMock()
    mock_existing.category_id = category_id
    mock_existing.name = "Science"
    mock_existing.description = "Original description"
    mock_existing.posts_count = 5
    mock_existing.created_at = datetime.utcnow()
    mock_existing.updated_at = None
    
    mock_updated = MagicMock()
    mock_updated.category_id = category_id
    mock_updated.name = "Updated Science"
    mock_updated.description = "Updated description"
    mock_updated.posts_count = 5
    mock_updated.created_at = mock_existing.created_at
    mock_updated.updated_at = datetime.utcnow()
    mock_updated._asdict.return_value = {
        "category_id": category_id,
        "name": "Updated Science",
        "description": "Updated description",
        "posts_count": 5,
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
    
    with patch("app.routes.categories.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.put(f"/api/categories/{category_id}", json=update_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["category_id"] == str(category_id)
        assert result["name"] == "Updated Science"
        assert result["description"] == "Updated description"
        assert "updated_at" in result

@pytest.mark.asyncio
async def test_update_category_not_found(client, mock_cassandra_session):
    """Test updating a non-existent category."""
    category_id = uuid4()
    
    update_data = {
        "name": "Updated Science",
        "description": "Updated description"
    }
    
    session_mock = MagicMock()
    
    mock_result = MagicMock()
    mock_result.one.return_value = None
    
    session_mock.execute.return_value = mock_result
    
    with patch("app.routes.categories.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.put(f"/api/categories/{category_id}", json=update_data)
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

@pytest.mark.asyncio
async def test_delete_category(client, mock_cassandra_session):
    """Test deleting a category."""
    category_id = uuid4()
    
    session_mock = MagicMock()
    
    existing_result = MagicMock()
    existing_result.one.return_value = MagicMock(category_id=category_id)
    
    session_mock.execute.side_effect = [
        existing_result,  
        MagicMock()       
    ]
    
    with patch("app.routes.categories.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.delete(f"/api/categories/{category_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["category_id"] == str(category_id)
        assert "Category deleted" in result["message"]

@pytest.mark.asyncio
async def test_delete_category_not_found(client, mock_cassandra_session):
    """Test deleting a non-existent category."""
    category_id = uuid4()
    
    session_mock = MagicMock()
    
    existing_result = MagicMock()
    existing_result.one.return_value = None
    
    session_mock.execute.return_value = existing_result
    
    with patch("app.routes.categories.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.delete(f"/api/categories/{category_id}")
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]