import asyncio
import json
import os
import time
import threading

from confluent_kafka import Consumer
from dotenv import load_dotenv
from app.indexes.forum_service.blog_posts import (
    BlogPostDocument, Category, Tag,
    CategoryDocument, TagDocument
)
from app.config import logger

load_dotenv()

es_client = None

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPICS = [
    os.getenv("KAFKA_FORUM_SN_BLOG_POSTS_TOPIC", "forum_sn.forum_keyspace.blog_posts"),
    os.getenv("KAFKA_FORUM_SN_CATEGORIES_TOPIC", "forum_sn.forum_keyspace.categories"),
    os.getenv("KAFKA_FORUM_SN_TAGS_TOPIC", "forum_sn.forum_keyspace.tags"),
]


def initialize_es_client():
    global es_client
    from app.main import app
    es_client = app.state.es_client


async def enrich_tags_and_categories(tag_ids, category_ids):
    """
    Retrieve TagDocument and CategoryDocument details from Elasticsearch
    for the given IDs.
    """
    enriched_tags = []
    enriched_categories = []

    tag_docs = await es_client.mget(
        index=TagDocument.Index.name,
        body={"ids": tag_ids}
    )
    cat_docs = await es_client.mget(
        index=CategoryDocument.Index.name,
        body={"ids": category_ids}
    )

    for doc in tag_docs.get("docs", []):
        if doc.get("found"):
            source = doc.get("_source", {})
            enriched_tags.append(
                Tag(tag_id=source.get("tag_id"), name=source.get("name"))
            )
        else:
            enriched_tags.append(
                Tag(tag_id=doc.get("_id"), name="")
            )

    for doc in cat_docs.get("docs", []):
        if doc.get("found"):
            source = doc.get("_source", {})
            enriched_categories.append(
                Category(category_id=source.get("category_id"), name=source.get("name"))
            )
        else:
            enriched_categories.append(
                Category(category_id=doc.get("_id"), name="")
            )
    return enriched_tags, enriched_categories


async def process_blog_post_record(payload):
    """
    Process a blog post record by looking up tag and category details
    from Elasticsearch (not in-memory caches) and embedding them as inner docs.
    """
    try:
        op = payload.get("op")
        after = payload.get("after")
        if op == "d":
            doc_id = after["post_id"]["value"]
            await es_client.delete(index=BlogPostDocument.Index.name, id=doc_id, ignore=[404])
            logger.info(f"Deleted blog post {doc_id} from index '{BlogPostDocument.Index.name}'.")
        else:
            doc_id = after["post_id"]["value"]
            author_id = after.get("author_id", {}).get("value")
            title = after.get("title", {}).get("value")
            content = after.get("content", {}).get("value")
            likes_count = after.get("likes_count", {}).get("value", 0)
            saves_count = after.get("saves_count", {}).get("value", 0)
            images = after.get("images", {}).get("value", [])
            created_at = after.get("created_at", {}).get("value")
            updated_at = after.get("updated_at", {})
            if updated_at:
                updated_at = updated_at.get("value")

            tag_ids = after.get("tags", {}).get("value", [])
            category_ids = after.get("categories", {}).get("value", [])

            enriched_tags, enriched_categories = await enrich_tags_and_categories(tag_ids, category_ids)

            new_doc = BlogPostDocument(
                meta={"id": doc_id},
                id=doc_id,
                author_id=author_id,
                title=title,
                content=content,
                likes_count=likes_count,
                saves_count=saves_count,
                images=images,
                created_at=created_at,
                updated_at=updated_at,
                tags=enriched_tags,
                categories=enriched_categories
            )
            await new_doc.save(using=es_client)
            logger.info(f"Upserted blog post {doc_id} into index '{BlogPostDocument.Index.name}'.")
    except Exception as e:
        logger.exception(f"Error processing blog post record: {e}")


async def update_blog_posts_for_tag(tag_id: str, tag_name: str):
    """
    Run an update_by_query on BlogPostDocument to update nested tag documents.
    """
    update_script = {
        "script": {
            "source": """
                if (ctx._source.tags != null) {
                  for (int i = 0; i < ctx._source.tags.size(); i++) {
                    if (ctx._source.tags[i].tag_id == params.tag_id) {
                      ctx._source.tags[i].name = params.tag_name;
                    }
                  }
                }
            """,
            "lang": "painless",
            "params": {"tag_id": tag_id, "tag_name": tag_name}
        },
        "query": {
            "nested": {
                "path": "tags",
                "query": {"term": {"tags.tag_id": tag_id}}
            }
        }
    }
    await es_client.update_by_query(index=BlogPostDocument.Index.name, body=update_script)
    logger.info(f"Updated tag {tag_id} in blog posts.")


async def update_blog_posts_for_category(category_id: str, category_name: str):
    """
    Run an update_by_query on BlogPostDocument to update nested category documents.
    """
    update_script = {
        "script": {
            "source": """
                if (ctx._source.categories != null) {
                  for (int i = 0; i < ctx._source.categories.size(); i++) {
                    if (ctx._source.categories[i].category_id == params.category_id) {
                      ctx._source.categories[i].name = params.category_name;
                    }
                  }
                }
            """,
            "lang": "painless",
            "params": {"category_id": category_id, "category_name": category_name}
        },
        "query": {
            "nested": {
                "path": "categories",
                "query": {"term": {"categories.category_id": category_id}}
            }
        }
    }
    await es_client.update_by_query(index=BlogPostDocument.Index.name, body=update_script)
    logger.info(f"Updated category {category_id} in blog posts.")


async def process_tag_record(payload):
    """
    Process tag records: update or delete the TagDocument and trigger update-by-query
    on blog posts.
    """
    try:
        op = payload.get("op")
        after = payload.get("after")
        tag_id = after["tag_id"]["value"]
        if op == "d":
            await es_client.delete(index=TagDocument.Index.name, id=tag_id, ignore=[404])
            logger.info(f"Deleted tag {tag_id} from TagDocument.")
            update_script = {
                "script": {
                    "source": """
                        if (ctx._source.tags != null) {
                          ctx._source.tags.removeIf(t -> t.tag_id == params.tag_id);
                        }
                    """,
                    "lang": "painless",
                    "params": {"tag_id": tag_id}
                },
                "query": {
                    "nested": {
                        "path": "tags",
                        "query": {"term": {"tags.tag_id": tag_id}}
                    }
                }
            }
            await es_client.update_by_query(index=BlogPostDocument.Index.name, body=update_script)
            logger.info(f"Removed tag {tag_id} from blog posts.")
        else:
            tag_name = after.get("name", {}).get("value", "")
            new_tag = TagDocument(tag_id=tag_id, name=tag_name)
            new_tag.meta.id = tag_id
            await new_tag.save(using=es_client)
            logger.info(f"Upserted tag {tag_id} into TagDocument.")
            await update_blog_posts_for_tag(tag_id, tag_name)
    except Exception as e:
        logger.exception(f"Error processing tag record: {e}")


async def process_category_record(payload):
    """
    Process category records: update or delete the CategoryDocument and trigger update-by-query
    on blog posts.
    """
    try:
        op = payload.get("op")
        after = payload.get("after")
        category_id = after["category_id"]["value"]
        if op == "d":
            await es_client.delete(index=CategoryDocument.Index.name, id=category_id, ignore=[404])
            logger.info(f"Deleted category {category_id} from CategoryDocument.")
            update_script = {
                "script": {
                    "source": """
                        if (ctx._source.categories != null) {
                          ctx._source.categories.removeIf(c -> c.category_id == params.category_id);
                        }
                    """,
                    "lang": "painless",
                    "params": {"category_id": category_id}
                },
                "query": {
                    "nested": {
                        "path": "categories",
                        "query": {"term": {"categories.category_id": category_id}}
                    }
                }
            }
            await es_client.update_by_query(index=BlogPostDocument.Index.name, body=update_script)
            logger.info(f"Removed category {category_id} from blog posts.")
        else:
            category_name = after.get("name", {}).get("value", "")
            new_category = CategoryDocument(
                meta={"id": category_id},
                category_id=category_id,
                name=category_name
            )
            await new_category.save(using=es_client)
            logger.info(f"Upserted category {category_id} into CategoryDocument.")
            await update_blog_posts_for_category(category_id, category_name)
    except Exception as e:
        logger.exception(f"Error processing category record: {e}")


async def process_record(record):
    """
    Dispatch CDC records to their corresponding processing function based on table name.
    """
    try:
        payload = record.get("payload", {})
        table_name = payload.get("source", {}).get("table")
        if table_name == "blog_posts":
            await process_blog_post_record(payload)
        elif table_name == "tags":
            await process_tag_record(payload)
        elif table_name == "categories":
            await process_category_record(payload)
        else:
            logger.warning(f"Unrecognized table: {table_name}")
    except Exception as e:
        logger.exception(f"Error processing record: {e}")


def start_consumer(loop: asyncio.AbstractEventLoop):
    consumer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "elasticsearch_forum_sn_group",
        "auto.offset.reset": "earliest",
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(KAFKA_TOPICS)
    logger.info(f"Subscribed to topics: {KAFKA_TOPICS}")

    global es_client
    if es_client is None:
        initialize_es_client()

    while True:
        try:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                logger.error(f"Consumer error: {message.error()}")
                continue
            record = json.loads(message.value().decode("utf-8"))
            asyncio.run_coroutine_threadsafe(process_record(record), loop)
            time.sleep(0.1)
        except Exception as e:
            logger.exception(f"Error in consumer loop: {e}")
            continue


def run_forum_sn_consumer(loop: asyncio.AbstractEventLoop):
    consumer_thread = threading.Thread(target=start_consumer, args=(loop,), daemon=True)
    consumer_thread.start()
    return consumer_thread
