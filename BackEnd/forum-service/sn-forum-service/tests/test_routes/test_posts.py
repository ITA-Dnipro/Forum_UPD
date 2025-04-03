import pytest
from httpx import AsyncClient
from app.schemas.post import PostResponse
from app.schemas.pagination import PaginatedResponse
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import json

@pytest.mark.asyncio
async def test_create_post(client, mock_cassandra_session):
    """Test creating a new post."""
    
    post_data = {
        "author_id": 1,
        "title": "Test Post",
        "content": "This is a test post",
        "categories": json.dumps([str(uuid4())]),
        "tags": json.dumps([str(uuid4())])
    }
    
    category_mock = MagicMock()
    category_mock.name = "Science"
    tag_mock = MagicMock()
    tag_mock.name = "Tech"
    
    mock_cassandra_session.configure_execute("INSERT INTO blog_posts", None)
    mock_cassandra_session.configure_execute("INSERT INTO posts_by_author", None)
    mock_cassandra_session.configure_execute("INSERT INTO posts_by_category", None)
    mock_cassandra_session.configure_execute("INSERT INTO posts_by_tag", None)
    mock_cassandra_session.configure_execute("SELECT name FROM categories", category_mock, 'one')
    mock_cassandra_session.configure_execute("SELECT name FROM tags", tag_mock, 'one')

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response = await ac.post("/api/posts/", data=post_data)
        
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_posts(client, mock_cassandra_session):
    post_id = uuid4()
    category_id = uuid4()
    tag_id = uuid4()
    
    rows_mock = MagicMock()
    
    row = MagicMock()
    row.post_id = post_id
    row.author_id = 1
    row.title = "Test Post"
    row.content = "Test content"
    row.images = ["/uploads/test.jpg"]
    row.categories = [category_id]
    row.tags = [tag_id]
    row.likes_count = 5
    row.dislikes_count = 2
    row.saves_count = 3
    row.comments = []
    row.created_at = datetime.utcnow()
    row.updated_at = None
    
    rows_mock.__iter__.return_value = [row]
    rows_mock.paging_state = None
    
    session_mock = MagicMock()
    
    session_mock.execute.return_value = rows_mock
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query.query_string if hasattr(query, 'query_string') else query
        
        if "SELECT * FROM blog_posts" in query_str:
            return rows_mock
        elif "categories WHERE category_id" in query_str:
            mock_category = MagicMock()
            mock_category.category_id = category_id
            mock_category.name = "Science"  
            result = MagicMock()
            result.one.return_value = mock_category
            return result
        elif "tags WHERE tag_id" in query_str:
            mock_tag = MagicMock()
            mock_tag.tag_id = tag_id
            mock_tag.name = "Tech"  
            result = MagicMock()
            result.one.return_value = mock_tag
            return result
        
        result = MagicMock()
        result.one.return_value = None
        return result
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get("/api/posts/?page_size=1")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 1
        assert result["items"][0]["title"] == "Test Post"

@pytest.mark.asyncio
async def test_get_post(client, mock_cassandra_session):
    post_id = uuid4()
    
    mock_row = MagicMock()
    mock_row.post_id = post_id
    mock_row.author_id = 1
    mock_row.title = "Single Post"
    mock_row.content = "Single content"
    mock_row.images = ["/uploads/single.jpg"]
    mock_row.categories = []  
    mock_row.tags = []  
    mock_row.likes_count = 10
    mock_row.dislikes_count = 1
    mock_row.saves_count = 2
    mock_row.comments = []
    mock_row.created_at = datetime.utcnow()
    mock_row.updated_at = None

    session_mock = MagicMock()
    execute_result = MagicMock()
    execute_result.one.return_value = mock_row
    session_mock.execute.return_value = execute_result
    
    with patch("app.routes.posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/posts/{post_id}")

        assert response.status_code == 200
        result = response.json()
        assert result["post_id"] == str(post_id)
        assert result["title"] == "Single Post"

@pytest.mark.asyncio
async def test_delete_post(client, mock_cassandra_session):
    post_id = uuid4()
    
    mock_existing = MagicMock()
    mock_existing.author_id = 1
    mock_existing.created_at = datetime.utcnow()
    
    session_mock = MagicMock()
    
    execute_result1 = MagicMock()
    execute_result1.one.return_value = mock_existing
    
    execute_result2 = MagicMock()
    execute_result3 = MagicMock()
    
    session_mock.execute.side_effect = [
        execute_result1,   
        execute_result2,  
        execute_result3   
    ]
    
    with patch("app.routes.posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.delete(f"/api/posts/{post_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["post_id"] == str(post_id)
        assert "Post deleted" in result["message"]

@pytest.mark.asyncio
async def test_get_posts_by_author(client, mock_cassandra_session):
    """Test retrieving posts by author."""
    author_id = 1
    post_id = uuid4()
    category_id = uuid4()
    tag_id = uuid4()
    
    mock_row = MagicMock()
    mock_row.post_id = post_id
    mock_row.title = "Author Post"
    mock_row.created_at = datetime.utcnow()

    mock_post_data = MagicMock()
    mock_post_data.post_id = post_id
    mock_post_data.author_id = author_id
    mock_post_data.title = "Author Post"
    mock_post_data.content = "Author content"
    mock_post_data.images = ["/uploads/author.jpg"]
    mock_post_data.categories = [category_id]
    mock_post_data.tags = [tag_id]
    mock_post_data.likes_count = 3
    mock_post_data.dislikes_count = 1
    mock_post_data.saves_count = 2
    mock_post_data.created_at = mock_row.created_at
    mock_post_data.updated_at = None
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query.query_string if hasattr(query, 'query_string') else query
        query_args = args[1] if len(args) > 1 else None
        
        if "SELECT post_id, title, created_at FROM posts_by_author WHERE author_id = %s" in query_str:
            posts_result = MagicMock()
            posts_result.__iter__.return_value = [mock_row]
            posts_result.paging_state = None
            return posts_result
        elif "SELECT * FROM blog_posts WHERE post_id = %s" in query_str:
            result = MagicMock()
            result.one.return_value = mock_post_data
            return result
        elif "SELECT name FROM categories WHERE category_id = %s" in query_str:
            mock_category = MagicMock()
            mock_category.name = "Science"  
            result = MagicMock()
            result.one.return_value = mock_category
            return result
        elif "SELECT name FROM tags WHERE tag_id = %s" in query_str:
            mock_tag = MagicMock()
            mock_tag.name = "Tech"  
            result = MagicMock()
            result.one.return_value = mock_tag
            return result
        
        result = MagicMock()
        result.one.return_value = None
        return result
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/posts/by-author/{author_id}?page_size=1")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 1
        assert result["items"][0]["title"] == "Author Post"