# app/utils/migrations.py
from app.services.cassandra import get_session
import logging

logger = logging.getLogger(__name__)

async def create_udt_types(session):
    """Створення користувацьких типів (UDT) у Cassandra"""
    session.execute("""
        CREATE TYPE IF NOT EXISTS comment_reply (
            id uuid,
            author_id int,
            content text,
            created_at timestamp,
            likes int,
            dislikes int
        );
    """)
    session.execute("""
        CREATE TYPE IF NOT EXISTS post_comment (
            id uuid,
            author_id int,
            content text,
            created_at timestamp,
            likes int,
            dislikes int,
            replies list<frozen<comment_reply>>
        );
    """)
    
    session.execute("""
        CREATE TYPE IF NOT EXISTS category_info (
            id uuid,
            name text
        );
    """)
    session.execute("""
        CREATE TYPE IF NOT EXISTS tag_info (
            id uuid,
            name text
        );
    """)

    session.execute("""
        CREATE TYPE IF NOT EXISTS image_info (
            url text
        );
    """)

async def create_tables(session):
    """Створення основних таблиць у Cassandra"""
    session.execute("""
        CREATE TABLE IF NOT EXISTS blog_posts (
            post_id uuid PRIMARY KEY,
            author_id int,
            title text,
            content text,
            likes_count int,      
            dislikes_count int,    
            saves_count int,      
            images list<text>,
            comments list<frozen<post_comment>>,
            categories list<uuid>,
            tags list<uuid>,
            created_at timestamp,
            updated_at timestamp
        );
    """)
    
    session.execute("""
        CREATE TABLE IF NOT EXISTS comment_replies (
            post_id uuid,
            comment_id uuid,
            reply_id uuid,
            author_id int,
            content text,
            created_at timestamp,
            likes int,
            dislikes int,
            PRIMARY KEY ((post_id, comment_id), reply_id)
        );
    """)
    
    session.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id uuid PRIMARY KEY,
            name text,
            description text,
            posts_count int,
            created_at timestamp,
            updated_at timestamp
        );
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tag_id uuid PRIMARY KEY,
            name text,
            description text,
            posts_count int,
            created_at timestamp,
            updated_at timestamp
        );
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS posts_by_author (
            author_id int,
            created_at timestamp,
            post_id uuid,
            title text,
            categories list<uuid>,
            tags list<uuid>,
            PRIMARY KEY (author_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS posts_by_category (
            category_id uuid,
            created_at timestamp,
            post_id uuid,
            title text,
            author_id int,
            PRIMARY KEY (category_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS posts_by_tag (
            tag_id uuid,
            created_at timestamp,
            post_id uuid,
            title text,
            author_id int,
            PRIMARY KEY (tag_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS saved_posts (
            user_id int,
            post_id uuid,
            saved_at timestamp,
            PRIMARY KEY (user_id, post_id)
        );
    """)
   
    session.execute("""
        CREATE TABLE IF NOT EXISTS post_likes (
            post_id uuid,
            user_id int,
            created_at timestamp,
            PRIMARY KEY (post_id, user_id)
        );
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS post_dislikes (
            post_id uuid,
            user_id int,
            created_at timestamp,
            PRIMARY KEY (post_id, user_id)
        );
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS comment_likes (
            post_id uuid,
            comment_id uuid,
            user_id int,
            created_at timestamp,
            PRIMARY KEY ((post_id, comment_id), user_id)
        );
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS comment_dislikes (
            post_id uuid,
            comment_id uuid,
            user_id int,
            created_at timestamp,
            PRIMARY KEY ((post_id, comment_id), user_id)
        );
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS comment_reply_likes (
            post_id uuid,
            comment_id uuid,
            reply_id uuid,
            user_id int,
            created_at timestamp,
            PRIMARY KEY ((post_id, comment_id, reply_id), user_id)
        );
    """)
    session.execute("""
        CREATE TABLE IF NOT EXISTS comment_reply_dislikes (
            post_id uuid,
            comment_id uuid,
            reply_id uuid,
            user_id int,
            created_at timestamp,
            PRIMARY KEY ((post_id, comment_id, reply_id), user_id)
        );
    """)

async def run_migrations():
    session = await get_session()
    logger.info("Creating UDT...")
    await create_udt_types(session)
    logger.info("Creating tables...")
    await create_tables(session)
    logger.info("Migration complete.")