# app/utils/migrations.py
from app.services.cassandra import get_session

import logging
logger = logging.getLogger(__name__)


async def create_udt_types(session):
    """Створення користувацьких типів (UDT) у Cassandra"""
    session.execute("""
        CREATE TYPE IF NOT EXISTS comment_reply (
            id int,
            author_id int,
            author_name text,
            content text,
            created_at timestamp,
            likes int,
            dislikes int
        );
    """)
    session.execute("""
        CREATE TYPE IF NOT EXISTS post_comment (
            id int,
            author_id int,
            author_name text,
            content text,
            created_at timestamp,
            likes int,
            dislikes int,
            replies list<frozen<comment_reply>>
        );
    """)
    session.execute("""
        CREATE TYPE IF NOT EXISTS answer_reply (
            id int,
            author_id int,
            author_name text,
            content text,
            created_at timestamp,
            likes int,
            dislikes int
        );
    """)
    session.execute("""
        CREATE TYPE IF NOT EXISTS question_answer (
            id int,
            author_id int,
            author_name text,
            content text,
            created_at timestamp,
            likes int,
            dislikes int,
            replies list<frozen<answer_reply>>
        );
    """)
    session.execute("""
        CREATE TYPE IF NOT EXISTS category_info (
            id int,
            name text
        );
    """)
    session.execute("""
        CREATE TYPE IF NOT EXISTS tag_info (
            id int,
            name text
        );
    """)

async def create_tables(session):
    """Створення основних таблиць у Cassandra"""
    session.execute("""
        CREATE TABLE IF NOT EXISTS blog_posts (
            post_id int PRIMARY KEY,
            author_id int,
            title text,
            content text,
            views_count int,
            likes_count int,
            images list<frozen<map<text, text>>>,
            comments list<frozen<post_comment>>,
            categories list<frozen<category_info>>,
            tags list<frozen<tag_info>>,
            created_at timestamp,
            updated_at timestamp
        );
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id int PRIMARY KEY,
            name text,
            description text,
            posts_count int,
            created_at timestamp,
            updated_at timestamp
        );
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tag_id int PRIMARY KEY,
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
            post_id int,
            title text,
            categories list<frozen<category_info>>,
            tags list<frozen<tag_info>>,
            PRIMARY KEY (author_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS posts_by_category (
            category_id int,
            created_at timestamp,
            post_id int,
            title text,
            author_id int,
            PRIMARY KEY (category_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS posts_by_tag (
            tag_id int,
            created_at timestamp,
            post_id int,
            title text,
            author_id int,
            PRIMARY KEY (tag_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS saved_posts (
            user_id int,
            created_at timestamp,
            post_id int,
            title text,
            PRIMARY KEY (user_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS liked_posts (
            user_id int,
            created_at timestamp,
            post_id int,
            title text,
            PRIMARY KEY (user_id, created_at, post_id)
        ) WITH CLUSTERING ORDER BY (created_at DESC);
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS post_likes (
            post_id int,
            user_id int,
            created_at timestamp,
            PRIMARY KEY (post_id, user_id)
        );
    """)

async def run_migrations():
    session = await get_session() 

    logger.info("Створення UDT...")
    await create_udt_types(session)
    
    logger.info("Створення таблиць...")
    await create_tables(session)  
    
    logger.info("Міграції завершено.")