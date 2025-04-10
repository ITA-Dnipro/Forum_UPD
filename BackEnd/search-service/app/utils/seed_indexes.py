from datetime import datetime

from faker import Faker

from ..config import logger
from ..indexes.event_service.events import EventDocument
from ..indexes.forum_service.blog_posts import BlogPostDocument
from ..indexes.forum_service.post_comments import PostCommentDocument
from ..indexes.forum_service.question_answers import QuestionAnswerDocument
from ..indexes.forum_service.questions import QuestionDocument
from ..indexes.news_service.news_article import NewsArticleDocument

faker = Faker()


async def seed_events():
    """Seed the events index if it's empty with some real-like data."""
    doc_count = await EventDocument.search().count()
    if doc_count == 0:
        logger.info("events index is empty. Seeding...")
        common_title_prefix = "Tech Conference: "
        common_content_prefix = "Join us for a deep dive into technology trends. "
        for i in range(5):
            title = f"{common_title_prefix}Event {i}" if i < 2 else f"Event {i}"
            content = (
                f"{common_content_prefix}{faker.text(max_nb_chars=150)}"
                if i < 2
                else faker.text(max_nb_chars=200)
            )
            doc = EventDocument(
                event_id=f"event_{i}",
                organizer_id=faker.random_int(min=1, max=100),
                title=title,
                content=content,
                categories=[{"category_id": faker.random_int(min=1, max=5), "name": faker.word()}],
                type=faker.random_element(elements=("online", "offline", "auction")),
                status=faker.random_element(elements=("active", "inactive")),
                location=faker.city(),
                image=faker.image_url(),
                available_slots=faker.random_int(min=10, max=100),
                capacity=100,
                date=datetime.now(),
                starting_time=datetime.now(),
            )
            await doc.save(index=EventDocument.get_index_name())
        logger.info("Finished seeding events.")
    else:
        logger.info("Events index already has data. Skipping...")


async def seed_blog_posts():
    """Seed the blog_posts index if it's empty with realistic content."""
    doc_count = await BlogPostDocument.search().count()
    if doc_count == 0:
        logger.info("blog_posts index is empty. Seeding...")
        common_title_prefix = "Insight: "
        common_content_prefix = "In today’s analysis, we explore the trends. "
        for i in range(5):
            title = f"{common_title_prefix}Blog Post {i}" if i < 2 else f"Blog Post {i}"
            content = (
                f"{common_content_prefix}{faker.text(max_nb_chars=200)}"
                if i < 2
                else faker.text(max_nb_chars=300)
            )
            doc = BlogPostDocument(
                id=f"blog_post_{i}",
                author_id=faker.random_int(min=1, max=50),
                title=title,
                content=content,
                likes_count=faker.random_int(min=0, max=100),
                saves_count=faker.random_int(min=0, max=50),
                categories=[{"category_id": faker.random_int(min=1, max=10), "name": faker.word()}],
                tags=[{"tag_id": faker.random_int(min=1, max=10), "name": faker.word()}],
                images=[faker.image_url()],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            await doc.save(index=BlogPostDocument.get_index_name())
        logger.info("Finished seeding blog_posts.")
    else:
        logger.info("blog_posts index already has data. Skipping...")


async def seed_post_comments():
    """Seed the blog_comments index if it's empty."""
    doc_count = await PostCommentDocument.search().count()
    if doc_count == 0:
        logger.info("blog_comments index is empty. Seeding...")
        common_content_prefix = "I completely agree: "
        for i in range(5):
            content = (
                f"{common_content_prefix}{faker.sentence()}"
                if i < 2
                else faker.sentence()
            )
            doc = PostCommentDocument(
                id=f"comment_{i}",
                author_id=str(faker.random_int(min=1, max=100)),
                content=content,
                likes_count=faker.random_int(min=0, max=50),
                dislikes_count=faker.random_int(min=0, max=10),
                created_at=datetime.now(),
            )
            await doc.save(index=PostCommentDocument.get_index_name())
        logger.info("Finished seeding blog_comments.")
    else:
        logger.info("blog_comments index already has data. Skipping...")


async def seed_question_answers():
    """Seed the question_answers index if it's empty with realistic data."""
    doc_count = await QuestionAnswerDocument.search().count()
    if doc_count == 0:
        logger.info("question_answers index is empty. Seeding...")
        common_content_prefix = "Based on my experience: "
        for i in range(5):
            content = (
                f"{common_content_prefix}{faker.text(max_nb_chars=200)}"
                if i < 2
                else faker.text(max_nb_chars=250)
            )
            doc = QuestionAnswerDocument(
                id=f"qa_{i}",
                author_id=str(faker.random_int(min=1, max=100)),
                author_name=faker.name(),
                content=content,
                likes_count=faker.random_int(min=0, max=50),
                dislikes_count=faker.random_int(min=0, max=10),
                is_accepted=faker.boolean(),
                created_at=datetime.now(),
            )
            await doc.save(index=QuestionAnswerDocument.get_index_name())
        logger.info("Finished seeding question_answers.")
    else:
        logger.info("question_answers index already has data. Skipping...")


async def seed_questions():
    """Seed the questions index if it's empty with real-like questions."""
    doc_count = await QuestionDocument.search().count()
    if doc_count == 0:
        logger.info("questions index is empty. Seeding...")
        common_title_prefix = "How do I: "
        for i in range(5):
            title = f"{common_title_prefix}Question {i}" if i < 2 else f"Question {i}"
            doc = QuestionDocument(
                id=f"question_{i}",
                author_id=str(faker.random_int(min=1, max=100)),
                title=title,
                content=faker.text(max_nb_chars=300),
                status=faker.random_element(elements=("open", "closed", "in_progress")),
                likes_count=faker.random_int(min=0, max=50),
                views_count=faker.random_int(min=0, max=1000),
                saves_count=faker.random_int(min=0, max=30),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            await doc.save(index=QuestionDocument.get_index_name())
        logger.info("Finished seeding questions.")
    else:
        logger.info("questions index already has data. Skipping...")


async def seed_news_articles():
    """Seed the news_articles index if it's empty with realistic news data."""
    doc_count = await NewsArticleDocument.search().count()
    if doc_count == 0:
        logger.info("news_articles index is empty. Seeding...")
        common_title_prefix = "Breaking News: "
        common_content_prefix = "In today's top story, "
        for i in range(5):
            title = f"{common_title_prefix}News article {i}" if i < 2 else f"News article {i}"
            content = (
                f"{common_content_prefix}{faker.text(max_nb_chars=300)}"
                if i < 2
                else faker.text(max_nb_chars=400)
            )
            doc = NewsArticleDocument(
                article_id=f"news_{i}",
                title=title,
                content=content,
                published_at=datetime.now(),
            )
            await doc.save(index=NewsArticleDocument.get_index_name())
        logger.info("Finished seeding news_articles.")
    else:
        logger.info("news_articles index already has data. Skipping...")


async def seed_all():
    """Wrapper to seed all indexes if they're empty."""
    await seed_events()
    await seed_blog_posts()
    await seed_post_comments()
    await seed_question_answers()
    await seed_questions()
    await seed_news_articles()
