import pytest
from httpx import AsyncClient
from app.schemas.pagination import PaginatedResponse
from app.schemas.post_reaction import PostReactionRequest, PostReactionResponse, PostReactionSummary
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import MagicMock, patch
import base64
import json

@pytest.mark.asyncio
async def test_add_reaction_like(client, mock_cassandra_session):
    """Test adding a like reaction to a post."""
    post_id = uuid4()
    user_id = 1
    
    reaction_request = {
        "user_id": user_id,
        "is_like": True
    }
    
    mock_post = MagicMock()
    mock_post.post_id = post_id
    mock_post.likes_count = 5
    mock_post.dislikes_count = 2
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT likes_count, dislikes_count FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post
            return post_result
        elif "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s" in query_str:
            likes_result = MagicMock()
            likes_result.one.return_value = None  
            return likes_result
        elif "SELECT user_id FROM post_dislikes WHERE post_id = %s AND user_id = %s" in query_str:
            dislikes_result = MagicMock()
            dislikes_result.one.return_value = None 
            return dislikes_result
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.post_reactions.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post(f"/api/posts/{post_id}/reactions", json=reaction_request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["post_id"] == str(post_id)
        assert result["user_id"] == user_id
        assert result["is_like"] == True
        assert "created_at" in result
        
        call_args_list = session_mock.execute.call_args_list
        likes_update_found = False
        for call in call_args_list:
            args = call[0]
            if isinstance(args[0], str) and "UPDATE blog_posts SET likes_count = %s" in args[0]:
                assert args[1][0] == 6  # 5 + 1
                likes_update_found = True
        assert likes_update_found, "likes_count update query not found"

@pytest.mark.asyncio
async def test_add_reaction_dislike(client, mock_cassandra_session):
    """Test adding a dislike reaction to a post."""
    post_id = uuid4()
    user_id = 1
    
    reaction_request = {
        "user_id": user_id,
        "is_like": False
    }
    
    mock_post = MagicMock()
    mock_post.post_id = post_id
    mock_post.likes_count = 5
    mock_post.dislikes_count = 2
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT likes_count, dislikes_count FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post
            return post_result
        elif "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s" in query_str:
            likes_result = MagicMock()
            likes_result.one.return_value = None 
            return likes_result
        elif "SELECT user_id FROM post_dislikes WHERE post_id = %s AND user_id = %s" in query_str:
            dislikes_result = MagicMock()
            dislikes_result.one.return_value = None  
            return dislikes_result
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.post_reactions.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post(f"/api/posts/{post_id}/reactions", json=reaction_request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["post_id"] == str(post_id)
        assert result["user_id"] == user_id
        assert result["is_like"] == False
        assert "created_at" in result
        
        call_args_list = session_mock.execute.call_args_list
        dislikes_update_found = False
        for call in call_args_list:
            args = call[0]
            if isinstance(args[0], str) and "UPDATE blog_posts SET dislikes_count = %s" in args[0]:
                assert args[1][0] == 3  # 2 + 1
                dislikes_update_found = True
        assert dislikes_update_found, "dislikes_count update query not found"

@pytest.mark.asyncio
async def test_add_reaction_switch_from_dislike_to_like(client, mock_cassandra_session):
    """Test switching reaction from dislike to like."""
    post_id = uuid4()
    user_id = 1
    
    reaction_request = {
        "user_id": user_id,
        "is_like": True
    }
    
    mock_post = MagicMock()
    mock_post.post_id = post_id
    mock_post.likes_count = 5
    mock_post.dislikes_count = 2
    
    mock_dislike = MagicMock()
    mock_dislike.user_id = user_id
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT likes_count, dislikes_count FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post
            return post_result
        elif "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s" in query_str:
            likes_result = MagicMock()
            likes_result.one.return_value = None  
            return likes_result
        elif "SELECT user_id FROM post_dislikes WHERE post_id = %s AND user_id = %s" in query_str:
            dislikes_result = MagicMock()
            dislikes_result.one.return_value = mock_dislike  
            return dislikes_result
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.post_reactions.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post(f"/api/posts/{post_id}/reactions", json=reaction_request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["is_like"] == True
        
        call_args_list = session_mock.execute.call_args_list
        
        dislike_delete_found = False
        for call in call_args_list:
            args = call[0]
            if isinstance(args[0], str) and "DELETE FROM post_dislikes" in args[0]:
                dislike_delete_found = True
        assert dislike_delete_found, "Delete dislike query not found"
        
        dislikes_decrement_found = False
        for call in call_args_list:
            args = call[0]
            if isinstance(args[0], str) and "UPDATE blog_posts SET dislikes_count = %s" in args[0]:
                assert args[1][0] == 1 
                dislikes_decrement_found = True
        assert dislikes_decrement_found, "dislikes_count decrement query not found"
        
        likes_increment_found = False
        for call in call_args_list:
            args = call[0]
            if isinstance(args[0], str) and "UPDATE blog_posts SET likes_count = %s" in args[0]:
                assert args[1][0] == 6  
                likes_increment_found = True
        assert likes_increment_found, "likes_count increment query not found"

@pytest.mark.asyncio
async def test_add_reaction_already_liked(client, mock_cassandra_session):
    """Test adding a like when user already liked."""
    post_id = uuid4()
    user_id = 1
    
    reaction_request = {
        "user_id": user_id,
        "is_like": True
    }
    
    mock_post = MagicMock()
    mock_post.post_id = post_id
    mock_post.likes_count = 5
    mock_post.dislikes_count = 2
    
    mock_like = MagicMock()
    mock_like.user_id = user_id
    
    session_mock = MagicMock()
    
    def execute_side_effect(*args, **kwargs):
        query = args[0]
        query_str = query if isinstance(query, str) else query.query_string
        
        if "SELECT likes_count, dislikes_count FROM blog_posts WHERE post_id = %s" in query_str:
            post_result = MagicMock()
            post_result.one.return_value = mock_post
            return post_result
        elif "SELECT user_id FROM post_likes WHERE post_id = %s AND user_id = %s" in query_str:
            likes_result = MagicMock()
            likes_result.one.return_value = mock_like  
            return likes_result
        
        return MagicMock()
    
    session_mock.execute.side_effect = execute_side_effect
    
    with patch("app.routes.post_reactions.get_session", return_value=session_mock):
        
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response = await ac.post(f"/api/posts/{post_id}/reactions", json=reaction_request)
        
        assert response.status_code == 400
        result = response.json()
        assert "already liked" in result["detail"]
