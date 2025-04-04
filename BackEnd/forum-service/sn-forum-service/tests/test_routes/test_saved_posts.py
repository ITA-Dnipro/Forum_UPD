import pytest
from httpx import AsyncClient
from app.schemas.pagination import PaginatedResponse
from app.schemas.post import PostResponse, SavePostRequest, UnsavePostRequest
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch
import base64

@pytest.mark.asyncio
async def test_get_saved_posts(client, mock_cassandra_session):
    """Test retrieving saved posts for a user."""
    user_id = 1
    post_id = uuid4()
    category_id = uuid4()
    tag_id = uuid4()
    
    mock_saved_row = MagicMock()
    mock_saved_row.post_id = post_id
    
    mock_post_row = MagicMock()
    mock_post_row.post_id = post_id
    mock_post_row.author_id = 2  
    mock_post_row.title = "Saved Post"
    mock_post_row.content = "This is a saved post"
    mock_post_row.images = ["/uploads/saved.jpg"]
    mock_post_row.categories = [{"id": str(category_id), "name": "Science"}]
    mock_post_row.tags = [{"id": str(tag_id), "name": "Python"}]
    mock_post_row.likes_count = 5
    mock_post_row.dislikes_count = 2
    mock_post_row.saves_count = 3
    mock_post_row.comments = []
    mock_post_row.created_at = datetime.utcnow()
    mock_post_row.updated_at = None
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query.query_string if hasattr(query, 'query_string') else query
        query_args = args[1] if len(args) > 1 else None
        
        if "SELECT post_id FROM saved_posts WHERE user_id = %s" in query_str:
            saved_result = MagicMock()
            saved_result.__iter__.return_value = [mock_saved_row]
            saved_result.paging_state = None
            return saved_result
        elif "SELECT * FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post_row
            return post_result
        elif "SELECT * FROM comment_replies" in query_str:
            replies_result = MagicMock()
            replies_result.all.return_value = []
            return replies_result
        
        result = MagicMock()
        result.one.return_value = None
        result.all.return_value = []
        return result
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.saved_posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/saved-posts/?user_id={user_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 1
        assert result["items"][0]["post_id"] == str(post_id)
        assert result["items"][0]["title"] == "Saved Post"

@pytest.mark.asyncio
async def test_get_saved_posts_empty(client, mock_cassandra_session):
    """Test retrieving saved posts when user has none."""
    user_id = 1
    
    session_mock = MagicMock()
    
    saved_result = MagicMock()
    saved_result.__iter__.return_value = []
    saved_result.paging_state = None
    
    session_mock.execute.return_value = saved_result
    
    with patch("app.routes.saved_posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/saved-posts/?user_id={user_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 0
        assert result["next_paging_state"] is None

@pytest.mark.asyncio
async def test_get_saved_posts_pagination(client, mock_cassandra_session):
    """Test retrieving saved posts with pagination."""
    user_id = 1
    post_id = uuid4()
    
    mock_saved_row = MagicMock()
    mock_saved_row.post_id = post_id
    
    mock_post_row = MagicMock()
    mock_post_row.post_id = post_id
    mock_post_row.author_id = 2
    mock_post_row.title = "Saved Post"
    mock_post_row.content = "This is a saved post"
    mock_post_row.images = ["/uploads/saved.jpg"]
    mock_post_row.categories = []
    mock_post_row.tags = []
    mock_post_row.likes_count = 5
    mock_post_row.dislikes_count = 2
    mock_post_row.saves_count = 3
    mock_post_row.comments = []
    mock_post_row.created_at = datetime.utcnow()
    mock_post_row.updated_at = None
    
    session_mock = MagicMock()
    
    saved_result = MagicMock()
    saved_result.__iter__.return_value = [mock_saved_row]
    saved_result.paging_state = b'next_page_token' 
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query.query_string if hasattr(query, 'query_string') else query
        
        if "SELECT post_id FROM saved_posts WHERE user_id = %s" in query_str:
            return saved_result
        elif "SELECT * FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post_row
            return post_result
        
        result = MagicMock()
        result.one.return_value = None
        result.all.return_value = []
        return result
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.saved_posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.get(f"/api/saved-posts/?user_id={user_id}&page_size=1")
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["items"]) == 1
        assert result["next_paging_state"] == base64.b64encode(b'next_page_token').decode('utf-8')

@pytest.mark.asyncio
async def test_save_post(client, mock_cassandra_session):
    """Test saving a post."""
    post_id = uuid4()
    user_id = 1
    
    save_request = {
        "user_id": user_id
    }
    
    mock_post_row = MagicMock()
    mock_post_row.post_id = post_id
    mock_post_row.saves_count = 5
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT post_id, saves_count FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post_row
            return post_result
        elif "SELECT user_id FROM saved_posts" in query_str:
            saved_result = MagicMock()
            saved_result.one.return_value = None  
            return saved_result
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.saved_posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post(f"/api/saved-posts/{post_id}/save", json=save_request)
        
        assert response.status_code == 200
        result = response.json()
        assert "Post saved successfully" in result["message"]
        
        call_args_list = session_mock.execute.call_args_list
        assert len(call_args_list) >= 4  
        
        update_query_found = False
        for call in call_args_list:
            args = call[0]
            if isinstance(args[0], str) and "UPDATE blog_posts" in args[0] and "saves_count" in args[0]:
                assert args[1][0] == 6  # 5 + 1
                update_query_found = True
        assert update_query_found, "saves_count update query not found"

@pytest.mark.asyncio
async def test_save_post_already_saved(client, mock_cassandra_session):
    """Test saving a post that's already saved."""
    post_id = uuid4()
    user_id = 1
    
    save_request = {
        "user_id": user_id
    }
    
    mock_post_row = MagicMock()
    mock_post_row.post_id = post_id
    mock_post_row.saves_count = 5
    
    mock_saved = MagicMock()
    mock_saved.user_id = user_id
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT post_id, saves_count FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post_row
            return post_result
        elif "SELECT user_id FROM saved_posts" in query_str:
            saved_result = MagicMock()
            saved_result.one.return_value = mock_saved  
            return saved_result
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.saved_posts.get_session", return_value=session_mock):
      
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post(f"/api/saved-posts/{post_id}/save", json=save_request)
        
        assert response.status_code == 409
        result = response.json()
        assert "already saved" in result["detail"]
        
        call_args_list = session_mock.execute.call_args_list
        for call in call_args_list:
            args = call[0]
            if isinstance(args[0], str) and "UPDATE blog_posts" in args[0] and "saves_count" in args[0]:
                assert False, "saves_count should not be updated when post already saved"

@pytest.mark.asyncio
async def test_save_post_not_found(client, mock_cassandra_session):
    """Test saving a post that doesn't exist."""
    post_id = uuid4()
    user_id = 1
    
    save_request = {
        "user_id": user_id
    }
    
    session_mock = MagicMock()
    
    post_result = MagicMock()
    post_result.one.return_value = None  
    
    session_mock.execute.return_value = post_result
    
    with patch("app.routes.saved_posts.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post(f"/api/saved-posts/{post_id}/save", json=save_request)
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower() 
