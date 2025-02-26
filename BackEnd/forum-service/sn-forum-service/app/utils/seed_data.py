# app/utils/seed_data.py
from datetime import datetime
from app.services.cassandra import get_session
import logging

logger = logging.getLogger(__name__)

def seed_database():
    session = get_session()
    
    try:
        categories = [
            {"id": 1, "name": "Technology"},
            {"id": 2, "name": "Programming"},
            {"id": 3, "name": "Design"}
        ]
        
        tags = [
            {"id": 1, "name": "Python"},
            {"id": 2, "name": "FastAPI"},
            {"id": 3, "name": "Web Development"}
        ]
        
        categories_list = [{"id": 1, "name": "Technology"}]
        tags_list = [{"id": 1, "name": "Python"}]
        
        session.execute("""
            INSERT INTO blog_posts (
                post_id, 
                author_id, 
                title, 
                content, 
                views_count, 
                likes_count, 
                categories, 
                tags, 
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            1,                          # post_id
            1,                          # author_id
            "Getting Started with FastAPI",  # title
            "FastAPI is a modern web framework...",  # content
            0,                          # views_count
            0,                          # likes_count
            categories_list,            # categories
            tags_list,                  # tags
            datetime.now()              # created_at
        ))
        
        logger.info("Seed completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during seeding: {str(e)}")
        raise